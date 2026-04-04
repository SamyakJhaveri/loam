# Phase 3: Augmentation Analysis & Story - Research

**Researched:** 2026-04-04
**Domain:** Data analysis, matplotlib visualization, LaTeX paper writing, statistical evidence from LLM augmentation evaluation results
**Confidence:** HIGH

## Summary

Phase 3 builds the per-kernel augmentation evidence from raw Qwen 3.5 397B eval result JSONs, identifies motivating examples or strengthens the null-result interpretation, produces two publication-quality figures, and writes 1-2 LASSI positioning paragraphs in paper.tex. All raw data exists on disk (624 augmented files + L0 baselines). The primary analysis covers 26 cuda-to-omp kernel pairs across all 5 suites (18 Rodinia + 5 HeCBench + 1 mixbench + 1 RSBench + 1 XSBench) at levels L0-L4.

Research reveals the data tells a "mostly null with interesting exceptions" story: 16 of 26 kernels are perfectly stable (same status at all 5 levels), 5 show PASS-to-FAIL degradation at specific levels (backprop, hotspot3d, lavamd, lud, scan), and 4 show surprising L0=FAIL-to-PASS improvements (bptree, mixbench, nn, streamcluster). Aggregate pass rates are flat (53.8%-65.4%), supporting the existing Cochran-Armitage null result. The exceptions are localized, not systematic.

**Primary recommendation:** Build a single `scripts/analysis/augmentation_analysis.py` script that reads all result JSONs, computes the per-kernel matrix, writes JSON+MD outputs, and generates both figures. Follow the exact pattern of `benchmark_characterization.py` (Phase 2). LASSI paragraphs go into paper.tex Section 7.4 (augmentation interpretation) as 1-2 paragraphs.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Primary matrix covers cuda-to-omp L0-L4 (as specified in AUG-01). This is the primary evaluation direction and has the most data (33 kernel pairs x 5 levels). **NOTE: Actual data shows 26 kernel pairs, not 33. See Data Correction below.**
- **D-02:** Secondary matrix covers ALL 7 directions with augmented data (624 total L1-L4 files across cuda-to-omp, omp-to-cuda, cuda-to-opencl, opencl-to-cuda, omp-to-opencl, opencl-to-omp, omp_target-to-cuda). Store in same JSON file as a separate section. Use secondary data to strengthen claims about direction-independence of the null result.
- **D-03:** L0 data comes from the standard (unaugmented) eval results -- same kernel pairs, no `-L` suffix in filename. Matrix must include L0 as the baseline column.
- **D-04:** "Mostly null with interesting exceptions" narrative. The Cochran-Armitage test (z=-0.17, p=0.87) already establishes the aggregate null result. Per-kernel evidence should STRENGTHEN this by showing the vast majority of kernels are stable, while calling out specific exceptions (e.g., backprop L3/L4 BUILD_FAIL) as localized phenomena, not systematic degradation.
- **D-05:** Investigate each exception to determine root cause -- is it a transform artifact (augmentation breaks compilation) or genuine model brittleness? This distinction matters for the paper claim. The backprop L3=BUILD_FAIL, L4=BUILD_FAIL pattern needs explanation.
- **D-06:** If exceptions are transform artifacts (augmentation engine issue, not model issue), note them as such and further strengthen the null-result interpretation. If genuine model brittleness, use as motivating examples per Niranjan's directive.
- **D-07:** Complementary framing, not adversarial. LASSI = agentic self-correction pipeline (80-85% on 10 HeCBench kernels). ParBench augmentation = robustness probing (does surface variation affect model capability?). These answer different research questions.
- **D-08:** Keep LASSI positioning brief -- 1-2 paragraphs in the augmentation discussion, not a full comparison table.
- **D-09:** Two figures total for augmentation (tight page budget): (1) Per-kernel x per-level heatmap, (2) Aggregate trend line with Wilson 95% CI error bars.
- **D-10:** Okabe-Ito color palette for all status categories. PDF + PNG output. Publication quality (matplotlib, no interactive).
- **D-11:** Figures go in `docs/paper/figures/` alongside existing paper figures. Generation script goes in `scripts/analysis/`.
- **D-12:** All augmentation analysis data goes into `results/analysis/augmentation_per_kernel_matrix.json` (as specified in AUG-01). Companion `.md` summary file alongside it.
- **D-13:** Follow Phase 2 pattern: single analysis script that computes all metrics and writes the combined JSON. Script in `scripts/analysis/augmentation_analysis.py`.

### Claude's Discretion
- JSON schema structure within the matrix file (section names, key organization)
- Exact matplotlib styling details beyond Okabe-Ito palette
- How to present secondary (non-cuda-to-omp) direction data in the summary
- Ordering of kernels in the heatmap (alphabetical, by pass rate, by SLoC)
- Whether to include confidence intervals on per-kernel cells or only on aggregates

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUG-01 | Per-kernel x per-level status matrix built from raw Qwen result JSONs (cuda-to-omp, L0-L4) and saved to results/analysis/augmentation_per_kernel_matrix.json | Full data inventory complete: 26 cuda-to-omp kernel pairs (18 Rodinia + 8 non-Rodinia), all have L0-L4 data. Result JSON schema documented. Filename conventions for L0 vs L1-L4 verified. |
| AUG-02 | 2-3 motivating examples identified (kernels showing PASS->FAIL degradation across levels) OR null-result interpretation strengthened with per-kernel evidence | 5 degradation patterns found (backprop, hotspot3d, lavamd, lud, scan). 4 improvement patterns found (bptree, mixbench, nn, streamcluster). 16/26 kernels perfectly stable. Root cause investigation needed for each exception. |
| AUG-03 | LASSI augmentation positioning paragraphs written (complementary, not competing) | LASSI content already well-covered in paper.tex lines 194-196 (related work) and line 1106 (implications). Augmentation positioning paragraphs go in Section 7.4 (augmentation-interpretation, line 1064). |
| AUG-04 | Augmentation trend graphs produced (per-kernel + aggregate, publication quality PDF+PNG, Okabe-Ito palette) | Existing F7 figure is a per-model line chart (Rodinia only, no CIs). Phase 3 produces: (1) new heatmap figure, (2) new aggregate trend figure with Wilson CIs. Can coexist with or replace F7. Okabe-Ito palette and scienceplots already in use. |
</phase_requirements>

## Data Correction (CRITICAL)

CONTEXT.md D-01 states "33 kernel pairs x 5 levels" for cuda-to-omp. **Actual data shows 26 kernel pairs, not 33.** Verified by listing all `*-cuda-to-*-omp-L*` files (excluding omp_target and stochastic samples) and extracting unique kernel pair stems.

The 26 cuda-to-omp kernel pairs with L0-L4 data:
- **Rodinia (18):** backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, kmeans, lavamd, lud, mummergpu, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster
- **HeCBench (5):** floydwarshall, heat2d, iso2dfd, scan, stencil1d
- **mixbench (1):** mixbench
- **RSBench (1):** rsbench
- **XSBench (1):** xsbench

The paper's existing Cochran-Armitage test uses n=16 (Rodinia-only, excluding kmeans and mummergpu KNOWN_FAIL). The Phase 3 matrix should include all 26 but clearly distinguish KNOWN_FAIL source specs in the matrix.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| matplotlib | 3.10.8 | Figure generation (heatmap, trend line) | Already in use by generate_paper_figures.py |
| scienceplots | (installed) | IEEE/science publication styles | Already in use (`plt.style.use(["science", "ieee", "no-latex"])`) |
| numpy | 2.4.3 | Numerical computation | Already in use across analysis scripts |
| scipy.stats | (with scipy) | Wilson CI computation, statistical tests | Already in use by statistical_analysis.py |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json (stdlib) | -- | Read result JSONs, write output JSON | All data I/O |
| re (stdlib) | -- | Filename parsing for augmentation levels | Level extraction from filenames |
| pathlib (stdlib) | -- | Path handling | Standard in all analysis scripts |
| argparse (stdlib) | -- | CLI argument parsing | `--project-root` flag |
| collections.defaultdict | -- | Group data by kernel/level/direction | Matrix construction |

No new packages needed. Everything is already available in the project's venv.

## Architecture Patterns

### Recommended Project Structure
```
scripts/analysis/
  augmentation_analysis.py          # NEW: single script for AUG-01 through AUG-04
  test_augmentation_analysis.py     # NEW: validation tests

results/analysis/
  augmentation_per_kernel_matrix.json  # NEW: primary output (AUG-01)
  augmentation_per_kernel_matrix.md    # NEW: companion markdown summary

docs/paper/figures/
  aug_heatmap.pdf / .png               # NEW: per-kernel x per-level heatmap (AUG-04)
  aug_trend.pdf / .png                 # NEW: aggregate trend with Wilson CIs (AUG-04)

docs/paper/latex/
  paper.tex                            # MODIFIED: LASSI positioning paragraphs (AUG-03)
```

### Pattern 1: Monolithic Analysis Script (from Phase 2)
**What:** Single script computes all metrics and writes combined JSON + MD output
**When to use:** When multiple related metrics share the same input data
**Example (from benchmark_characterization.py):**
```python
#!/usr/bin/env python3
"""scripts/analysis/augmentation_analysis.py

Complete augmentation analysis for the SC26 ParBench paper.
Computes 4 metrics (AUG-01 through AUG-04) from raw eval result JSONs.

Output: results/analysis/augmentation_per_kernel_matrix.json + .md
        docs/paper/figures/aug_heatmap.{pdf,png}
        docs/paper/figures/aug_trend.{pdf,png}

Usage:
    python3 scripts/analysis/augmentation_analysis.py \
        --project-root /home/samyak/Desktop/parbench_sam
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ... rest of script
```

### Pattern 2: Result JSON Loading (from generate_paper_data.py)
**What:** Parse augmentation level from filename, load overall_status, group by kernel/level/direction
**Key conventions:**
```python
def _augment_level_from_filename(stem: str) -> int:
    """Extract augmentation level from result file stem.
    Convention: {src_id}-to-{tgt_id}-L{N}.json -> N
                {src_id}-to-{tgt_id}.json      -> 0  (L0)
    """
    m = re.search(r"-L(\d+)(?:-s\d+)?$", stem)
    return int(m.group(1)) if m else 0

# CRITICAL: use overall_status, NOT run_status
status = data.get("overall_status", "UNKNOWN")

# Skip stochastic samples (filename ends with -s{N})
if re.search(r"-s\d+$", stem):
    continue
```

### Pattern 3: Wilson CI for Error Bars (from statistical_analysis.py)
**What:** Wilson score 95% CI for binomial proportions
**Why:** Standard in the project for all pass rate CIs
```python
from scipy import stats as sp_stats
import math

def wilson_ci(passes: int, total: int, alpha: float = 0.05) -> dict:
    z = sp_stats.norm.ppf(1 - alpha / 2)
    p_hat = passes / total
    denom = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denom
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total) / denom
    return {
        "rate": round(p_hat, 4),
        "ci_lower": round(max(0.0, center - spread), 4),
        "ci_upper": round(min(1.0, center + spread), 4),
        "n": total,
    }
```

### Pattern 4: Okabe-Ito Status Colors (from generate_paper_figures.py)
**What:** Colorblind-safe palette for status categories
**Already defined -- reuse exactly:**
```python
STATUS_COLORS: dict[str, str] = {
    "PASS":            "#009E73",   # green
    "BUILD_FAIL":      "#D55E00",   # vermillion
    "RUN_FAIL":        "#E69F00",   # orange
    "VERIFY_FAIL":     "#0072B2",   # blue
    "EXTRACTION_FAIL": "#CC79A7",   # purple
}
```

### Pattern 5: Figure Save (from generate_paper_figures.py)
**What:** Dual PDF+PNG save
```python
def _save_figure(fig, output_dir, stem):
    for fmt in ("png", "pdf"):
        path = output_dir / f"{stem}.{fmt}"
        fig.savefig(path, format=fmt, dpi=300 if fmt == "png" else None)
        print(f"  Saved: {path}")
```

### Pattern 6: IEEE/Science Style Setup
```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401
plt.style.use(["science", "ieee", "no-latex"])
```

### Anti-Patterns to Avoid
- **Do NOT modify existing generate_paper_figures.py F7:** Phase 3 produces NEW figures (heatmap + trend), not modifications to the existing F7 augmentation robustness figure. F7 may be superseded later, but Phase 3 should not touch it.
- **Do NOT modify result JSONs:** Results are immutable (project invariant).
- **Do NOT use `run_status` for verdicts:** Always use `overall_status` (see known-issues.md "Eval Result JSON Schema Quirk").
- **Do NOT include KNOWN_FAIL in Cochran-Armitage recomputation:** The paper's existing test deliberately excludes KNOWN_FAIL source specs. The Phase 3 matrix should include ALL 26 pairs but annotate KNOWN_FAIL separately.
- **Do NOT hardcode n=33 or n=16:** Use actual data on disk to determine kernel pair count dynamically.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wilson confidence intervals | Custom CI formula | `wilson_ci()` from statistical_analysis.py or re-implement identically | Already verified in the project, used everywhere |
| Filename parsing for aug levels | Ad-hoc string splitting | `_augment_level_from_filename()` pattern from generate_paper_data.py | Handles edge cases (L0 = no suffix, stochastic samples) |
| Heatmap coloring | Custom color mapping | matplotlib `ListedColormap` with `STATUS_COLORS` dict | Standard colorblind-safe palette already defined |
| IEEE figure styling | Custom rcParams | `scienceplots` with `["science", "ieee", "no-latex"]` | Matches all existing paper figures |
| KNOWN_FAIL exclusion list | Inline list | Import from `generate_paper_data.py EXCLUDED_SPECS` or define identical frozenset | Canonical list, prevents drift |

## Raw Data Inventory (HIGH confidence -- verified against disk)

### Primary Matrix: cuda-to-omp L0-L4

Full matrix verified from raw result JSONs:

| Kernel | Suite | L0 | L1 | L2 | L3 | L4 | Pattern |
|--------|-------|----|----|----|----|----|----|
| backprop | rodinia | PASS | PASS | PASS | BUILD_FAIL | BUILD_FAIL | **Degradation** |
| bfs | rodinia | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| bptree | rodinia | BUILD_FAIL | RUN_FAIL | RUN_FAIL | PASS | BUILD_FAIL | **Improvement** |
| cfd | rodinia | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| floydwarshall | hecbench | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| heartwall | rodinia | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | Stable FAIL |
| heat2d | hecbench | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| hotspot | rodinia | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| hotspot3d | rodinia | PASS | BUILD_FAIL | PASS | PASS | PASS | **Degradation** (single-level) |
| iso2dfd | hecbench | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| kmeans | rodinia | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | Stable FAIL (KNOWN_FAIL src) |
| lavamd | rodinia | PASS | BUILD_FAIL | BUILD_FAIL | VERIFY_FAIL | PASS | **Degradation** (multi-level) |
| lud | rodinia | PASS | PASS | BUILD_FAIL | RUN_FAIL | PASS | **Degradation** (mid-level) |
| mixbench | mixbench | BUILD_FAIL | BUILD_FAIL | PASS | BUILD_FAIL | BUILD_FAIL | **Improvement** (single-level) |
| mummergpu | rodinia | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | Stable FAIL (KNOWN_FAIL src) |
| myocyte | rodinia | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | VERIFY_FAIL | BUILD_FAIL | Mostly stable FAIL |
| nn | rodinia | BUILD_FAIL | PASS | PASS | BUILD_FAIL | PASS | **Improvement** (non-monotonic) |
| nw | rodinia | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| particlefilter | rodinia | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| pathfinder | rodinia | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| rsbench | rsbench | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | Stable FAIL |
| scan | hecbench | PASS | BUILD_FAIL | PASS | PASS | PASS | **Degradation** (single-level) |
| srad | rodinia | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| stencil1d | hecbench | PASS | PASS | PASS | PASS | PASS | Stable PASS |
| streamcluster | rodinia | BUILD_FAIL | BUILD_FAIL | PASS | BUILD_FAIL | BUILD_FAIL | **Improvement** (single-level) |
| xsbench | xsbench | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | Stable FAIL |

### Aggregate Pass Rates
| Level | Pass | Total | Rate |
|-------|------|-------|------|
| L0 | 16 | 26 | 61.5% |
| L1 | 14 | 26 | 53.8% |
| L2 | 17 | 26 | 65.4% |
| L3 | 14 | 26 | 53.8% |
| L4 | 16 | 26 | 61.5% |

### Classification Summary
- **Stable PASS (10):** bfs, cfd, floydwarshall, heat2d, hotspot, iso2dfd, nw, particlefilter, pathfinder, srad, stencil1d (actually 11 -- stencil1d included)
- **Stable FAIL (5):** heartwall, kmeans, mummergpu, rsbench, xsbench
- **Degradation (5):** backprop, hotspot3d, lavamd, lud, scan -- kernels that PASS at L0 but FAIL at some higher level
- **Improvement (4):** bptree, mixbench, nn, streamcluster -- kernels that FAIL at L0 but PASS at some higher level
- **Other (1):** myocyte (mostly stable FAIL with one VERIFY_FAIL at L3)

### Secondary Data: All 7 Directions
| Direction | L0 | L1 | L2 | L3 | L4 |
|-----------|----|----|----|----|-----|
| cuda-to-omp | 16/26 (62%) | 14/26 (54%) | 17/26 (65%) | 14/26 (54%) | 16/26 (62%) |
| omp-to-cuda | 14/26 (54%) | 12/26 (46%) | 12/26 (46%) | 14/26 (54%) | 11/26 (42%) |
| cuda-to-opencl | 4/23 (17%) | 5/23 (22%) | 5/23 (22%) | 3/23 (13%) | 3/23 (13%) |
| opencl-to-cuda | 2/23 (9%) | 2/23 (9%) | 1/23 (4%) | 1/23 (4%) | 0/23 (0%) |
| omp-to-opencl | 6/20 (30%) | 4/20 (20%) | 6/20 (30%) | 6/20 (30%) | 3/20 (15%) |
| opencl-to-omp | 7/20 (35%) | 6/20 (30%) | 7/20 (35%) | 8/20 (40%) | 7/20 (35%) |
| omp_target-to-cuda | 6/9 (67%) | 6/9 (67%) | 7/9 (78%) | 8/9 (89%) | 7/9 (78%) |
| cuda-to-omp_target | 0/7 (0%) | 3/7 (43%) | 1/7 (14%) | 1/7 (14%) | 1/7 (14%) |

## Common Pitfalls

### Pitfall 1: CONTEXT.md Kernel Count Mismatch
**What goes wrong:** CONTEXT says "33 kernel pairs" but actual data has 26 for cuda-to-omp
**Why it happens:** The 33 figure may have been estimated from Rodinia (18) + other suites without precise counting, or may include directions beyond cuda-to-omp
**How to avoid:** Always derive counts dynamically from data on disk. Never hardcode expected counts.
**Warning signs:** Any assertion of n=33 in code or output

### Pitfall 2: Conflating "Balanced" and "Full" Subsets
**What goes wrong:** Paper's existing Cochran-Armitage test uses n=16 (Rodinia-only, KNOWN_FAIL excluded). Phase 3 matrix uses n=26 (all suites, KNOWN_FAIL included). Mixing these will produce inconsistent claims.
**Why it happens:** `generate_paper_data.py` filters with `--suite rodinia` and excludes KNOWN_FAIL. Phase 3 has no such filter.
**How to avoid:** The Phase 3 matrix should include ALL 26 kernel pairs with a `known_fail` flag. Aggregate statistics should clearly state whether they include or exclude KNOWN_FAIL. The existing Cochran-Armitage (n=16) should NOT be recomputed with n=26 without careful discussion -- the paper already states the n=16 result.
**Warning signs:** Pass rates that don't match paper_data.json values

### Pitfall 3: Stochastic Sample Contamination
**What goes wrong:** Including `-s0.json`, `-s1.json`, `-s2.json` files in the matrix (these are temperature=0.7 pass@k samples)
**Why it happens:** Glob patterns like `*-cuda-to-*-omp*.json` match stochastic files too
**How to avoid:** Always filter out files matching `-s\d+` suffix before processing
**Warning signs:** More than 5 files per kernel-direction pair

### Pitfall 4: omp_target vs omp Confusion
**What goes wrong:** Files like `hecbench-convolution1d-cuda-to-hecbench-convolution1d-omp_target.json` get included in cuda-to-omp analysis
**Why it happens:** The string "omp" is a substring of "omp_target"
**How to avoid:** Use precise filename matching. The target API is the last segment of the target spec ID. Check for `omp_target` explicitly before checking for `omp`.
**Warning signs:** Finding 7+ HeCBench cuda-to-omp pairs (should be 5; the other 5 are cuda-to-omp_target)

### Pitfall 5: Claiming Augmentation "Causes" Failure
**What goes wrong:** Stating that augmentation causes backprop L3/L4 to fail, when the actual cause is the LLM producing different (worse) code when given augmented input
**Why it happens:** Conflating "the augmented prompt led to a worse translation" with "augmentation broke the code"
**How to avoid:** The augmentation engine is validated separately (68/88 specs PASS at L1-L4 -- this is the harness-level test in `results/augmentation/rodinia_aug_results.json`). LLM degradation at specific levels means the LLM produced different code, not that augmentation corrupted the source.
**Warning signs:** Phrases like "augmentation breaks compilation" in the analysis narrative

### Pitfall 6: Figure Naming Collision with F7
**What goes wrong:** Overwriting the existing `f7_augmentation_robustness.{pdf,png}` which is referenced in paper.tex
**Why it happens:** The existing F7 covers augmentation robustness; Phase 3 figures also cover augmentation
**How to avoid:** Use distinct figure names: `aug_heatmap.{pdf,png}` and `aug_trend.{pdf,png}`. These are NEW figures, not replacements for F7.
**Warning signs:** `\includegraphics{f7_augmentation_robustness.pdf}` in paper.tex breaks

## Code Examples

### Loading Result JSONs and Building Matrix
```python
# Source: generate_paper_data.py pattern adapted for augmentation matrix
import json, re
from pathlib import Path
from collections import defaultdict

EXCLUDED_SPECS = frozenset({
    "rodinia-kmeans-cuda", "rodinia-mummergpu-cuda", "rodinia-mummergpu-omp",
    "rodinia-hybridsort-cuda", "rodinia-nn-opencl", "rodinia-kmeans-opencl",
})

def build_cuda_to_omp_matrix(results_dir: Path) -> dict:
    """Build per-kernel x per-level status matrix for cuda-to-omp."""
    matrix = defaultdict(dict)
    
    for f in sorted(results_dir.glob("*.json")):
        stem = f.stem
        # Skip stochastic samples
        if re.search(r"-s\d+$", stem):
            continue
        # Must be X-cuda-to-X-omp pattern (not omp_target, not opencl)
        if "-cuda-to-" not in stem:
            continue
        # Extract target API -- last segment after last hyphen in target spec
        # ... precise API extraction logic needed
        
        data = json.load(open(f))
        level = data.get("augment_level")
        if level is None:
            level = _augment_level_from_filename(stem)
        
        kernel = data.get("kernel", "unknown")
        suite = data.get("source_spec", "").split("-")[0]
        status = data.get("overall_status", "UNKNOWN")
        source_spec = data.get("source_spec", "")
        
        matrix[kernel]["suite"] = suite
        matrix[kernel]["source_spec"] = source_spec
        matrix[kernel]["known_fail"] = source_spec in EXCLUDED_SPECS
        matrix[kernel][f"L{level}"] = status
    
    return dict(matrix)
```

### Heatmap Figure (per-kernel x per-level)
```python
# Source: generate_paper_figures.py patterns, adapted for heatmap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
import scienceplots  # noqa: F401

plt.style.use(["science", "ieee", "no-latex"])

STATUS_COLORS = {
    "PASS":        "#009E73",
    "BUILD_FAIL":  "#D55E00",
    "RUN_FAIL":    "#E69F00",
    "VERIFY_FAIL": "#0072B2",
}

def generate_heatmap(matrix, output_dir):
    """Per-kernel x per-level heatmap for cuda-to-omp."""
    # Map statuses to integers for colormap
    status_to_int = {"PASS": 0, "BUILD_FAIL": 1, "RUN_FAIL": 2, "VERIFY_FAIL": 3}
    colors = [STATUS_COLORS[s] for s in ["PASS", "BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL"]]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)
    
    # Build 2D array: kernels (rows) x levels (columns)
    kernels = sorted(matrix.keys())
    levels = ["L0", "L1", "L2", "L3", "L4"]
    data_array = []
    for k in kernels:
        row = [status_to_int.get(matrix[k].get(l, "UNKNOWN"), -1) for l in levels]
        data_array.append(row)
    
    fig, ax = plt.subplots(figsize=(3.5, 6))
    im = ax.imshow(data_array, cmap=cmap, norm=norm, aspect="auto")
    
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels(levels)
    ax.set_yticks(range(len(kernels)))
    ax.set_yticklabels(kernels, fontsize=7)
    
    # Add status text annotations in cells
    for i, k in enumerate(kernels):
        for j, l in enumerate(levels):
            status = matrix[k].get(l, "?")
            abbrev = {"PASS": "P", "BUILD_FAIL": "BF", "RUN_FAIL": "RF", "VERIFY_FAIL": "VF"}.get(status, "?")
            ax.text(j, i, abbrev, ha="center", va="center", fontsize=6, color="white" if status != "PASS" else "black")
    
    # Legend
    legend_elements = [Patch(facecolor=c, label=s) for s, c in STATUS_COLORS.items()]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=7)
    
    _save_figure(fig, output_dir, "aug_heatmap")
    plt.close(fig)
```

### Aggregate Trend Line with Wilson CIs
```python
def generate_trend_line(matrix, output_dir):
    """Aggregate pass rate trend L0-L4 with Wilson 95% CI error bars."""
    levels = [0, 1, 2, 3, 4]
    level_labels = ["L0", "L1", "L2", "L3", "L4"]
    
    rates, ci_lowers, ci_uppers = [], [], []
    for level in levels:
        key = f"L{level}"
        total = sum(1 for k in matrix if key in matrix[k])
        passes = sum(1 for k in matrix if matrix[k].get(key) == "PASS")
        ci = wilson_ci(passes, total)
        rates.append(ci["rate"] * 100)
        ci_lowers.append((ci["rate"] - ci["ci_lower"]) * 100)
        ci_uppers.append((ci["ci_upper"] - ci["rate"]) * 100)
    
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.errorbar(levels, rates, yerr=[ci_lowers, ci_uppers],
                fmt="o-", color=OKABE_ITO["blue"], capsize=4, linewidth=1.8, markersize=7,
                label="Pass Rate (Wilson 95% CI)")
    
    ax.set_xticks(levels)
    ax.set_xticklabels(level_labels)
    ax.set_xlabel("Augmentation Level")
    ax.set_ylabel("Pass Rate (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", fontsize=8)
    
    _save_figure(fig, output_dir, "aug_trend")
    plt.close(fig)
```

### LASSI Positioning Paragraph (for paper.tex)
```latex
% Insert in Section 7.4 (augmentation-interpretation), after existing content
% Source: D-07, D-08 from CONTEXT.md

ParBench's augmentation and LASSI's self-correction pipeline address complementary
research questions. LASSI~\cite{LASSI2024} measures the effectiveness of an
agentic correction loop---how much can iterative error feedback improve translation
success? ParBench's augmentation measures robustness---does surface-level code
variation affect translation capability? The Cochran-Armitage null result
($z = -0.17$, $p = 0.87$) demonstrates that augmentation is a diagnostic tool:
it confirms that ParBench measures genuine translation capability rather than
training-data recall, but it does not discriminate between augmentation levels.
LASSI's self-correction, by contrast, produces a measurable lift (15--30
percentage points) by addressing the structural errors that dominate ParBench's
failure taxonomy. The two capabilities are complementary: augmentation validates
the benchmark, while agentic correction improves the translation.
```

## JSON Schema Recommendation (Claude's Discretion)

Recommended structure for `augmentation_per_kernel_matrix.json`:

```json
{
  "generated_at": "2026-04-04T...",
  "data_source": "results/evaluation/together-qwen-3.5-397b-a17b/",
  "primary_matrix": {
    "direction": "cuda-to-omp",
    "levels": ["L0", "L1", "L2", "L3", "L4"],
    "kernel_count": 26,
    "known_fail_excluded_count": 2,
    "per_kernel": {
      "backprop": {
        "suite": "rodinia",
        "source_spec": "rodinia-backprop-cuda",
        "known_fail": false,
        "L0": "PASS", "L1": "PASS", "L2": "PASS", "L3": "BUILD_FAIL", "L4": "BUILD_FAIL",
        "pattern": "degradation",
        "pass_count": 3,
        "total_levels": 5
      }
    },
    "aggregate": {
      "L0": {"pass": 16, "total": 26, "rate": 0.6154, "ci_lower": 0.0, "ci_upper": 0.0},
      "L1": {"pass": 14, "total": 26, "rate": 0.5385, "ci_lower": 0.0, "ci_upper": 0.0}
    },
    "aggregate_excl_known_fail": {
      "L0": {"pass": 14, "total": 24, "rate": 0.5833},
      "L1": {"pass": 12, "total": 24, "rate": 0.5000}
    },
    "pattern_summary": {
      "stable_pass": ["bfs", "cfd", "..."],
      "stable_fail": ["heartwall", "kmeans", "..."],
      "degradation": ["backprop", "hotspot3d", "lavamd", "lud", "scan"],
      "improvement": ["bptree", "mixbench", "nn", "streamcluster"],
      "other": ["myocyte"]
    },
    "exceptions": [
      {
        "kernel": "backprop",
        "pattern": "degradation",
        "l0_status": "PASS",
        "degraded_levels": {"L3": "BUILD_FAIL", "L4": "BUILD_FAIL"},
        "root_cause": "..."
      }
    ]
  },
  "secondary_matrix": {
    "directions": ["cuda-to-omp", "omp-to-cuda", "cuda-to-opencl", "..."],
    "per_direction_aggregate": {
      "cuda-to-omp": {"L0": {"pass": 16, "total": 26, "rate": 0.6154}, "...": "..."},
      "omp-to-cuda": {"L0": {"pass": 14, "total": 26, "rate": 0.5385}, "...": "..."}
    }
  }
}
```

## Heatmap Ordering Recommendation (Claude's Discretion)

Order kernels in the heatmap by pattern, then alphabetically within each pattern group:
1. Stable PASS kernels (top) -- the "green band" visually reinforces the null result
2. Degradation kernels -- the exceptions readers should focus on
3. Improvement kernels -- surprising counter-examples
4. Stable FAIL kernels (bottom) -- uniformly red, provides context but not the focus

This ordering makes the visual narrative clear: most of the heatmap is green (stable), with a small band of exceptions in the middle, and a band of consistently failing kernels at the bottom.

## Existing Paper Content Map

The paper already has significant augmentation content. Phase 3 adds to -- does not replace -- existing text:

| Section | Line | Current Content | Phase 3 Action |
|---------|------|-----------------|----------------|
| Abstract | 68 | Cochran-Armitage z=-0.17, p=0.87 | No change |
| S1 Introduction | 116 | "Level-invariant: 68 of 88 non-KNOWN_FAIL specs..." | No change |
| S2 Related Work | 194-196 | LASSI comparison (purpose + methodology) | No change |
| S4.3 Augmentation Engine | 313-354 | Transform descriptions, level table, baseline | No change |
| S5.3 Augmentation Protocol | 628-633 | Protocol description, seed=42, 480 tasks | No change |
| S6.5 Augmentation Robustness | 864-901 | Table + F7 figure + Cochran-Armitage | **Add references to new figures/matrix** |
| S7.4 Augmentation Interpretation | 1064-1072 | Null result interpretation, 3 implications | **Add LASSI positioning paragraphs (AUG-03), add per-kernel evidence references** |
| S7.6 Implications | 1102 | "Augmentation should be standard practice" | No change |

## Backprop L3/L4 BUILD_FAIL Root Cause (D-05 Investigation)

The backprop L3 result JSON shows the build error is a **linker error**: `multiple definition of 'gettime'` and `multiple definition of 'main'` between `backprop.o` and `backprop_kernel.o`. This means the LLM produced a `backprop_kernel.c` that duplicated function definitions from `backprop.c`.

This is NOT a transform artifact (the augmentation engine is validated separately -- backprop-cuda PASSES augmentation at all levels in `rodinia_aug_results.json`). This is **genuine model brittleness**: when the LLM receives augmented source (L3/L4 density), it produces a translation that duplicates functions across files. The augmented surface caused the model to make a different (worse) structural decision.

**Implication for narrative (D-06):** Backprop is a genuine motivating example of model brittleness exposed by augmentation. It shows that while the aggregate null result holds, individual kernels can degrade -- and the degradation reveals structural weaknesses in the model's multi-file translation strategy.

## Relationship to Existing F7 Figure

The existing F7 (`f7_augmentation_robustness.{pdf,png}`) is a per-model line chart of pass rates by level for Rodinia cuda-to-omp only. It supports the multi-model comparison in Section 6.5.

Phase 3 produces two NEW figures:
1. **aug_heatmap**: Per-kernel x per-level heatmap (all suites, cuda-to-omp). This is the primary evidence figure showing individual kernel stability/instability.
2. **aug_trend**: Aggregate trend line with Wilson CIs (all suites, cuda-to-omp). This is the statistical summary figure with error bars.

These complement F7. The planner should decide whether F7 is superseded (and its `\includegraphics` replaced) or whether all three coexist. Given the tight page budget (D-09 says "two figures total for augmentation"), the heatmap and trend line likely replace F7. But this is a paper-assembly decision for Phase 5, not Phase 3.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | pyproject.toml (pytest section) |
| Quick run command | `python3 -m pytest scripts/analysis/test_augmentation_analysis.py -x -v` |
| Full suite command | `python3 -m pytest scripts/analysis/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUG-01 | Matrix JSON has correct structure, kernel count, level values | unit | `python3 -m pytest scripts/analysis/test_augmentation_analysis.py::test_matrix_structure -x` | Wave 0 |
| AUG-01 | Matrix kernel count matches actual result files on disk | integration | `python3 -m pytest scripts/analysis/test_augmentation_analysis.py::test_kernel_count_matches_disk -x` | Wave 0 |
| AUG-01 | overall_status values match raw JSON files | integration | `python3 -m pytest scripts/analysis/test_augmentation_analysis.py::test_status_values_match_raw -x` | Wave 0 |
| AUG-02 | Degradation patterns correctly identified | unit | `python3 -m pytest scripts/analysis/test_augmentation_analysis.py::test_pattern_classification -x` | Wave 0 |
| AUG-03 | manual-only | Manual: verify LASSI paragraphs in paper.tex Section 7.4 | N/A (LaTeX text) | N/A |
| AUG-04 | Figure files exist in expected formats | smoke | `python3 -m pytest scripts/analysis/test_augmentation_analysis.py::test_figures_exist -x` | Wave 0 |
| AUG-04 | Figures use Okabe-Ito palette colors | unit | `python3 -m pytest scripts/analysis/test_augmentation_analysis.py::test_okabe_ito_palette -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest scripts/analysis/test_augmentation_analysis.py -x -v`
- **Per wave merge:** `python3 -m pytest scripts/analysis/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `scripts/analysis/test_augmentation_analysis.py` -- covers AUG-01 through AUG-04
- [ ] Framework install: None needed -- pytest 9.0.2 already available

## Sources

### Primary (HIGH confidence)
- Raw result JSONs in `results/evaluation/together-qwen-3.5-397b-a17b/` -- all 26 cuda-to-omp L0-L4 + 624 total augmented files verified on disk
- `c_augmentation/augment_dataset.py` line 111 -- LEVEL_FRACTIONS = {1: 0.0, 2: 0.33, 3: 0.66, 4: 1.0}
- `scripts/generate_paper_figures.py` lines 44-81 -- Okabe-Ito palette and STATUS_COLORS definitions
- `scripts/analysis/statistical_analysis.py` lines 112-142 -- Wilson CI implementation
- `scripts/analysis/generate_paper_data.py` lines 657-721 -- Augmentation analysis pattern
- `scripts/analysis/benchmark_characterization.py` -- Phase 2 monolithic script pattern
- `docs/paper/latex/paper.tex` lines 864-901 (S6.5), 1064-1072 (S7.4) -- existing augmentation paper content
- `results/analysis/paper_data.json` > primary_campaign.augmentation -- existing n=16 Cochran-Armitage result
- `results/augmentation/rodinia_aug_results.json` -- harness-level augmentation validation (60 entries)

### Secondary (MEDIUM confidence)
- CONTEXT.md canonical references -- data inventory verified against disk except n=33 correction to n=26

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all packages verified installed, versions checked
- Architecture: HIGH - all patterns are from existing codebase files, verified
- Data inventory: HIGH - full matrix computed from raw JSONs on disk
- Pitfalls: HIGH - based on actual data mismatches discovered during research (n=33 vs n=26, balanced subset scope)

**Research date:** 2026-04-04
**Valid until:** 2026-04-08 (paper deadline -- data is frozen)
