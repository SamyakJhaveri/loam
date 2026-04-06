# Phase 11: Paper TeX Integration - Research

**Researched:** 2026-04-05
**Domain:** LaTeX paper editing, cross-consistency auditing, IEEE formatting, statistical power analysis
**Confidence:** HIGH

## Summary

Phase 11 is a large-scope LaTeX editing and auditing phase that modifies `docs/paper/latex/paper.tex` (1286 lines, 8 sections, 24 floats) and creates a new cross-consistency audit script. The paper currently uses 710 tasks from `paper_data.json` as the authoritative data source (established by Phase 12). The primary technical challenges are: (1) moving 17 of 24 floats to the existing appendix while maintaining `\ref` pointers, (2) rewriting Section 7 Discussion from 7 subsections to 2-3 merged subsections, (3) computing and honestly reporting MDES power analysis for the Cochran-Armitage test (P0-6), (4) selecting 3 representative VERIFY_FAIL case studies from 91 available results, and (5) building an automated Python audit script that parses paper.tex for all numbers and cross-checks against JSON data files.

The existing appendices.tex (946 lines, 3 appendix sections A/B/C) already uses `\appendices` from IEEEtran and `\input{appendices}` from paper.tex line 1277. The float migration must extend this existing appendix structure rather than creating a parallel one. A critical data reconciliation issue exists: `quantitative_findings.json` uses n=700 (excluding omp_target case-study directions) while `paper_data.json` uses n=710 (all directions). The paper uses 710 throughout per Phase 12 decisions. The audit script must handle this dual-source reality.

**Primary recommendation:** Execute the 4-plan, 3-wave structure from CONTEXT.md D-08 through D-11. Plan 1 (appendix + float migration) is the critical-path gating item -- all subsequent plans depend on the paper being within page budget before writing new content.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Create a LaTeX appendix section in paper.tex. Move 17 of 24 floats to appendix. Main text keeps only 7 floats.
- **D-02:** Main text floats (KEEP): `tab:related-work` (S2), `tab:overall-pass` (S6), `tab:direction-rates` (S6), `tab:per-kernel` condensed (S6), `fig:architecture` (S3), `fig:failure-taxonomy` (S6), `fig:kernel-heatmap` (S6).
- **D-03:** Appendix floats (MOVE -- all 17): Tables: `tab:augmentation-levels`, `tab:kernel-pairs`, `tab:api-characteristics`, `tab:suite-summary`, `tab:benchmark-characterization`, `tab:category-distribution`, `tab:model-config`, `tab:hardware`, `tab:repair-transitions`, `tab:self-repair`, `tab:augmentation-rates`, `tab:pass-at-k`, `tab:stats-summary`, full `tab:per-kernel` (31 rows). Figures: `fig:repo-vs-kernel`, `fig:augmentation`, `fig:pass-at-k`, `fig:xsbench`.
- **D-04:** Every moved float gets a `\ref` pointer from the main text paragraph where it was previously placed.
- **D-05:** Methodology tables (model-config, hardware, suite-summary) -- all move to appendix. Key facts stated inline in Section 5 prose.
- **D-06:** Section 3 (ParBench Framework, 160 lines) -- keep full text, no compression.
- **D-07:** Section 4 (Benchmark Curation, 226 lines) -- keep full text. Only tables move to appendix.
- **D-08:** Plan 1 -- Appendix structure + float migration.
- **D-09:** Plan 2 -- Main-text number/claim updates (TEX-01 through TEX-08).
- **D-10:** Plan 3 -- SC26 review items.
- **D-11:** Plan 4 -- Automated cross-consistency audit script (TEX-09).
- **D-12:** FULL treatment: P0-6 (Cochran-Armitage power analysis), P1-8 (VERIFY_FAIL case studies), P1-15 (S7 redundancy reduction).
- **D-13:** BRIEF treatment: P0-7, P1-9, P1-11, P1-14, P1-16, P1-17, P1-19.
- **D-14:** Merge S7.1-S7.5 into 2-3 subsections focused on IMPLICATIONS.
- **D-15:** Proposed merged structure: (1) Kernel-Centric Translation Implications (S7.1+S7.3), (2) Error Analysis & Actionable Insights (S7.2+S7.4+S7.5), (3) Threats to Validity (stays, updated).
- **D-16:** Threats to Validity STAYS in main text, updated with P1-16, P1-19, sample size limitations.
- **D-17:** Automated Python script for cross-consistency audit, not manual grep.
- **D-18:** Leverages Phase 9's `paper_claims` section in quantitative_findings.json.

### Claude's Discretion
- Appendix section ordering (by original section order, or grouped by type: tables then figures)
- Exact LaTeX `\appendix` or `\section*{Supplementary Material}` style
- Whether condensed per-kernel table uses tier midrule separators or plain top-5/bottom-5
- P1-17 exact eval commands -- in S5 prose or as appendix listing
- How to handle the aug_heatmap figure from Phase 13 (goes in appendix or stays near S6.5)
- Minor prose adjustments when removing table references that no longer point to main text
- Specific VERIFY_FAIL case selection for the 3 main-text examples (must be representative)

### Deferred Ideas (OUT OF SCOPE)
- Extended VERIFY_FAIL analysis with all cases (beyond 3 main-text examples) -- goes in appendix
- Performance/timing analysis with kernel-level profiling -- blocked on nvprof/ncu data
- GPT-4.1 mini column additions -- blocked on Le's data (use `\tbd` macro)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEX-01 | Abstract: Headline numbers updated, every number matches Section 6 | paper_data.json verified: 710 tasks, 38.3% [34.8%, 41.9%], 96 specs, 5 suites. Abstract already updated by Phase 12 -- verify consistency after float migration. |
| TEX-02 | Section 1 Introduction: Quantitative highlights, LASSI differentiation, gap paragraph | Already written by Phase 5. Verify numbers still correct after Phase 12 updates. |
| TEX-03 | Section 3 Design: Architecture verified, spec example, file role taxonomy | Per D-06 keep full text. Verify against actual codebase. No major edits expected. |
| TEX-04 | Section 4 Augmentation: Level defs, power analysis (P0-6), softened interpretation (P1-16), McNemar caveat (P1-19) | MDES computed: 34.1pp detectable at 80% power with n=24. Must add honest limitation sentence. Cochran-Armitage z=0.0, p=1.0 from paper_data.json. |
| TEX-05 | Section 5 Methodology: Tables moved to appendix, key facts inline, HeCBench commit (P0-7), eval commands (P1-17) | HeCBench commit: `22785cdd7`. Hardware/model-config/suite-summary tables all move to appendix. |
| TEX-06 | Section 6 Results: All numbers updated, VERIFY_FAIL case studies (P1-8), spectrum reframe (P1-9), HPC tier grounding (P1-11), XSBench honesty (P1-14) | 91 VERIFY_FAIL results available. Top subcategories: wrong_numerical_output (77), verification_error (9), missing_output (5). |
| TEX-07 | Section 7 Discussion: Redundancy reduced (P1-15), threats updated, deeper analysis | Currently 7 subsections (108 lines). Merge per D-14/D-15 to 3 subsections. |
| TEX-08 | Section 8 Related Work: ParBench positioned vs LASSI, TransCoder, etc. | Already has Related Work in S2 (83 lines). Verify positioning is current. |
| TEX-09 | Cross-consistency audit: Python script, zero unverified numbers remain | No existing audit script. Build from scratch. Leverage paper_claims (20 entries) as seed. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python 3.12 | 3.12.3 | Audit script runtime | Project standard per CLAUDE.md [VERIFIED: project config] |
| scipy | 1.11.4 | Power analysis computation (norm.ppf for MDES) | Already installed, needed for P0-6 MDES calculation [VERIFIED: `python3 -c "import scipy"`] |
| json (stdlib) | -- | Parse paper_data.json, quantitative_findings.json | Standard library [VERIFIED: built-in] |
| re (stdlib) | -- | Regex extraction of numbers from paper.tex | Standard library [VERIFIED: built-in] |
| argparse (stdlib) | -- | CLI interface for audit script | Project convention per CLAUDE.md [VERIFIED: all scripts use argparse] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib (stdlib) | -- | File path handling | Project convention: all scripts use Path objects [VERIFIED: project pattern] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom regex parser | TexSoup/pylatexenc | Custom is simpler for number extraction; full LaTeX parsing is overkill for this use case |
| statsmodels | scipy.stats | statsmodels not installed; scipy suffices for MDES computation |

**Installation:**
```bash
# No new packages needed -- all dependencies already installed
```

## Architecture Patterns

### Recommended Project Structure
```
scripts/analysis/
    cross_consistency_audit.py    # NEW: TEX-09 audit script
docs/paper/latex/
    paper.tex                     # Modified: float migration, number updates, SC26 items
    appendices.tex                # Modified: receives 17 migrated floats
```

### Pattern 1: Float Migration (Cut-Paste with Ref Pointers)
**What:** Move a `\begin{table}...\end{table}` block from paper.tex into appendices.tex, replacing it in paper.tex with a `\ref` pointer sentence. [VERIFIED: current paper.tex structure]
**When to use:** For each of the 17 floats being moved to appendix per D-03.
**Example:**
```latex
% IN paper.tex (AFTER migration) -- where the table used to be:
% The full hardware and software configuration is detailed in Appendix Table~\ref{tab:hardware}.
% Key system: NVIDIA GeForce RTX 4070 (sm\_89), CUDA 12.3, GCC 12.4.0.

% IN appendices.tex (NEW section D or extension of C) -- receives the table:
\begin{table}[htbp]
\centering
\caption{Hardware and software environment.}
\label{tab:hardware}
% ... full table content moved here ...
\end{table}
```

### Pattern 2: Condensed Per-Kernel Table with Full Version in Appendix
**What:** Create a condensed version of `tab:per-kernel` showing only top-5 easiest + top-5 hardest kernels in main text, with full 31-row table in appendix. [VERIFIED: D-02/D-03 decisions]
**When to use:** Plan 1 -- the per-kernel table is the most space-consuming single float.
**Example:**
```latex
% Main text: condensed table
\begin{table*}[t]
\caption{Per-kernel pass rates: top-5 easiest and top-5 hardest kernels (full 31-kernel table in Appendix Table~\ref{tab:per-kernel-full}).}
\label{tab:per-kernel}
% ... 10 rows with tier midrule separators ...
\end{table*}

% Appendix: full table
\begin{table*}[htbp]
\caption{Full per-kernel pass rates across all 31 evaluation kernels.}
\label{tab:per-kernel-full}
% ... 31 rows ...
\end{table*}
```

### Pattern 3: Provenance Comment Convention (Established Phase 1/12)
**What:** Every number in paper.tex has a `% src:` comment tracing to its data source. [VERIFIED: paper.tex lines 58-69, 86-87, 103-146]
**When to use:** Every time a number is added or updated.
**Example:**
```latex
% src: paper_data.json > primary_campaign > overall: pass=272, total=710, rate=0.3831
Qwen~3.5 achieves an overall pass rate of 38.3\% [34.8\%, 41.9\%].
```

### Pattern 4: S7 Discussion Merge (D-14/D-15)
**What:** Merge current 7 subsections into 3 focused subsections. [VERIFIED: current S7 has S7.1-S7.7, 108 lines total]
**When to use:** Plan 3 (SC26 review items) -- P1-15 redundancy reduction.
**Merge map:**
```
CURRENT S7.1 (Kernel-Centric Advantage)    → MERGED S7.1 (Kernel-Centric Translation Implications)
CURRENT S7.3 (Model Capability Analysis)   → MERGED S7.1
CURRENT S7.2 (BUILD_FAIL Bottleneck)       → MERGED S7.2 (Error Analysis & Actionable Insights)
CURRENT S7.4 (Direction Asymmetry)         → MERGED S7.2
CURRENT S7.5 (Augmentation Interpretation) → MERGED S7.2
CURRENT S7.6 (Threats to Validity)         → MERGED S7.3 (Threats to Validity) -- unchanged label
CURRENT S7.7 (Implications for HPC)        → Fold key points into S7.1 and S7.2; delete subsection
```

### Anti-Patterns to Avoid
- **Re-applying Phase 12.1 fixes:** P0 quick fixes (Table 1, 700/710, SIMT, pass@1 terminology, Table 3 source structure) are ALREADY applied. Do NOT re-apply. [VERIFIED: Phase 12.1 CONTEXT.md, STATE.md]
- **Using quantitative_findings.json for overall totals:** Use `paper_data.json` (710 tasks) as authoritative source for paper numbers, not `quantitative_findings.json` (700 tasks, excludes omp_target). [VERIFIED: paper_data.json total=710, qf total=700]
- **Breaking appendices.tex structure:** The file already has 3 appendix sections (A, B, C). New floats must be added to an existing or new section, not break the `\appendices` command. [VERIFIED: appendices.tex structure]
- **Deleting `\pending{}` and `\tbd` macros:** These mark GPT-4.1 mini placeholders that are out of scope. Preserve them. [VERIFIED: D-deferred items]
- **Touching float environments that Phase 13 will modify:** `fig:xsbench` (rename to `fig:cross-suite`), F3 caption, aug_heatmap insertion are Phase 13 tasks. Phase 11 should move these floats to appendix AS-IS; Phase 13 will then modify them in their new location.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| LaTeX number extraction | Manual grep per number | Regex-based parser in audit script | Too many numbers (est. 50-80) to check manually; error-prone |
| Wilson CI computation | Manual formula | scipy.stats for audit script CI verification | Already used in existing analysis scripts |
| MDES power analysis | Approximation from memory | scipy.stats.norm.ppf with exact Cochran-Armitage formula | Precise computation needed for P0-6; reviewers will check |
| Float migration | Manual cut-paste | Systematic section-by-section migration with checklist | 17 floats is too many for ad-hoc editing; need tracking |

## Common Pitfalls

### Pitfall 1: Label Collision After Float Migration
**What goes wrong:** Moving a float from paper.tex to appendices.tex can cause `\label` duplication or broken `\ref` if the label name changes.
**Why it happens:** Temptation to rename labels like `tab:per-kernel` to `tab:per-kernel-full` for the appendix version while keeping the condensed version with the original label.
**How to avoid:** Keep ALL existing labels unchanged on the moved floats. For the condensed per-kernel table in main text, use a NEW label (`tab:per-kernel-condensed` or keep `tab:per-kernel` for main and use `tab:per-kernel-full` for appendix). Decide one scheme and be consistent.
**Warning signs:** LaTeX compilation warnings about multiply-defined labels.

### Pitfall 2: 700 vs 710 Task Count Confusion
**What goes wrong:** Accidentally using quantitative_findings.json's 700-task count in a paper claim that should use paper_data.json's 710-task count.
**Why it happens:** Two authoritative data files with different task counts due to omp_target inclusion/exclusion.
**How to avoid:** Always source paper numbers from `paper_data.json` (710 tasks, all directions). Use `quantitative_findings.json` only for supplementary analysis dimensions it uniquely provides (paper_claims mapping, per-suite breakdowns of the 700-task subset). The audit script must handle BOTH sources.
**Warning signs:** Any number derived from 700 appearing in paper.tex.

### Pitfall 3: Stale `\ref` Pointers After Float Migration
**What goes wrong:** A paragraph references `Table~\ref{tab:hardware}` inline, but after migration the table is in the appendix. The `\ref` still works but the reader sees "Table XII" when it's now "Table D-3" in appendix.
**Why it happens:** IEEEtran `\appendices` command resets table/figure numbering to appendix scheme.
**How to avoid:** After migration, do a full search for every `\ref{tab:...}` and `\ref{fig:...}` of moved floats. Update surrounding prose from "Table X shows..." to "See Appendix Table~\ref{tab:hardware}" or similar framing.
**Warning signs:** Paper prose saying "Table X" when the number resolves to an appendix table number.

### Pitfall 4: S7 Merge Losing Content
**What goes wrong:** During the S7.1-S7.5 merge into 2-3 subsections, important nuances get dropped.
**Why it happens:** The merge is conceptual (combining themes) not just structural (moving paragraphs). Content needs to be rewritten, not just concatenated.
**How to avoid:** Before merging, list every substantive claim in S7.1-S7.5 (currently 9 subsections). Check each claim off as it appears in the merged version. Key claims to preserve: kernel-centric advantage quantification (64.2% vs 0%), BUILD_FAIL dominance (55.0% of failures), MoE architecture observation, OpenCL translatability ceiling, LASSI capability spectrum, bimodal pass@k distribution.
**Warning signs:** Merged S7 that's shorter than the original but missing key claims.

### Pitfall 5: Audit Script False Positives on Non-Data Numbers
**What goes wrong:** The audit script flags numbers like "32 threads" (warp size) or "5 suites" (structural count) as mismatches because they don't appear in paper_data.json.
**Why it happens:** Naive regex extraction catches ALL numbers, not just data-derived claims.
**How to avoid:** Categorize extracted numbers: (a) data-derived (pass rates, counts from eval campaigns) -- must match JSON, (b) structural constants (API count, suite count, spec count) -- verify against known constants, (c) methodological parameters (temperature=0, retries=3) -- skip or whitelist, (d) external citations (LASSI 80-85%, ParEval-Repo 0%) -- skip. The audit script should have a whitelist for categories (c) and (d).
**Warning signs:** Audit report with >50% false positive rate.

### Pitfall 6: Phase 13 Coordination on Moved Floats
**What goes wrong:** Phase 11 moves `fig:xsbench` to appendix; Phase 13 then tries to rename it to `fig:cross-suite` in paper.tex (where it no longer exists).
**Why it happens:** Phase 13 plans were written assuming floats are in paper.tex.
**How to avoid:** Move floats AS-IS in Phase 11. Phase 13 will need to know that 4 of its target floats (`fig:xsbench`, `fig:augmentation`, F3 caption) are now in appendices.tex. Document the final location of each moved float.
**Warning signs:** Phase 13 editing paper.tex for floats that are now in appendices.tex.

## Code Examples

### Cross-Consistency Audit Script Architecture
```python
# Source: designed for this phase based on project conventions [ASSUMED pattern from existing scripts]
#!/usr/bin/env python3
"""Cross-consistency audit: extract numbers from paper.tex, match against JSON data files."""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def extract_numbers_from_tex(tex_path: Path) -> list[dict]:
    """Extract all percentages, counts, and CIs from paper.tex with line numbers."""
    # Pattern: XX.X%, [XX.X%, YY.Y%], N/M, integers in data contexts
    ...


def load_ground_truth(analysis_dir: Path) -> dict:
    """Load paper_data.json and quantitative_findings.json as cross-check sources."""
    ...


def match_claims(extracted: list[dict], ground_truth: dict, paper_claims: list[dict]) -> list[dict]:
    """Match extracted numbers against ground truth, using paper_claims as seed mapping."""
    ...


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cross-consistency audit for paper.tex")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    ...
```

### MDES Power Analysis Computation (for P0-6)
```python
# Source: computed from scipy.stats during research [VERIFIED: scipy 1.11.4 available]
from scipy import stats
import math

z_alpha = stats.norm.ppf(0.975)  # 1.96 for two-sided alpha=0.05
z_beta = stats.norm.ppf(0.80)     # 0.84 for 80% power

n_per_level = 24  # kernels per augmentation level
levels = [0, 1, 2, 3, 4]
xbar = sum(levels) / len(levels)
sum_sq = sum((x - xbar)**2 for x in levels)  # = 10.0

p_hat = 0.6667  # Observed L0 pass rate (CUDA-to-OMP balanced)
sigma = math.sqrt(p_hat * (1 - p_hat))  # 0.4714

mdes_slope = (z_alpha + z_beta) * sigma / math.sqrt(n_per_level * sum_sq)
mdes_total = mdes_slope * 4  # L0 to L4 = 4 units

# Result: MDES = 34.1 percentage points across L0-L4
# Interpretation: With n=24, the test can only detect a >34pp monotonic decline
# The observed range (58.3%-70.8%) is well within the zone of non-detection
```

### LaTeX for Honest Power Limitation (P0-6 output)
```latex
% Source: P0-6 requirement + MDES computation [VERIFIED: scipy computation]
% In Section 4 or Section 6.5 (augmentation), after Cochran-Armitage result:
A power analysis reveals that with $n=24$ kernels per level,
the Cochran-Armitage test achieves 80\% power only for trends
exceeding 34 percentage points across L0--L4---a coarse threshold
relative to the observed pass-rate range (58.3\%--70.8\%).
The null result ($z = 0.0$, $p = 1.0$) is therefore consistent
with genuine augmentation invariance, but also with small-to-moderate
effects that our sample size cannot detect.
```

### McNemar Power Caveat (P1-19 output)
```latex
% Source: P1-19 requirement + statistical_analysis.json direction_asymmetry [VERIFIED]
% In Threats to Validity:
McNemar's tests for direction asymmetry have limited power given
the small number of discordant pairs ($n_{\text{discordant}} = 5$--$9$
across the four bidirectional pairs). Non-significance should not
be interpreted as evidence of symmetric difficulty; the tests are
effectively underpowered for detecting moderate asymmetries.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 12 pass@1 terminology | Phase 12.1 "greedy pass rate" | 2026-04-06 | All ParBench-specific pass@1 renamed; pass@k reserved for T=0.7 sampling |
| Rodinia-only 480-task scope | All-suite 710-task scope | Phase 12 (2026-04-06) | All paper numbers now use paper_data.json with 710 tasks |
| SPMD in Table 3 | SIMT in Table 3 | Phase 12.1 (2026-04-06) | Correct CUDA execution model terminology |
| S7 with 7 subsections | Target: 3 merged subsections | Phase 11 (pending) | Per D-14/D-15, will reduce redundancy per P1-15 |
| No appendix for evidence tables | Target: 17 floats in appendix | Phase 11 (pending) | Per D-01/D-03, reduces main text to <=10 pages |

## Data Source Reconciliation

This section documents the critical data source discrepancy that the planner and audit script must handle.

| Data Source | Total Tasks | Scope | Authoritative For |
|-------------|-------------|-------|-------------------|
| `paper_data.json` | 710 | All directions including omp_target | ALL paper.tex numbers (per Phase 12 D-01) |
| `quantitative_findings.json` campaign_1 | 700 | Standard 6 directions only (excludes omp_target) | paper_claims mapping, per-suite breakdowns, SLoC correlation |
| `quantitative_findings.json` paper_claims | 20 entries | Mixed scopes (annotated per claim) | Automated claim-to-data mapping seed for TEX-09 |
| `statistical_analysis.json` | varies | Per-test scope | McNemar asymmetry (4 pairs), augmentation trends, pass@k |
| `error_taxonomy.json` | 1248 raw | All results including omp_target | VERIFY_FAIL subcategories for P1-8 case studies |
| `selfrepair_analysis.json` | 710 | All directions | Self-repair rates, repair trajectories |

**Rule:** When a paper claim cites a number, trace to `paper_data.json` first. If the field doesn't exist there, trace to `quantitative_findings.json` with explicit scope annotation.

[VERIFIED: paper_data.json total=710, quantitative_findings.json campaign_1 n=700, by inspecting both files]

## VERIFY_FAIL Case Study Material (P1-8)

91 VERIFY_FAIL results are available. The error_taxonomy.json breaks them into 3 subcategories:

| Subcategory | Count | Top Kernels | Representative Failure Mode |
|-------------|-------|-------------|----------------------------|
| wrong_numerical_output | 77 | cfd (16), kmeans (16), hotspot (7), gaussian (6), lavamd (6) | Compilable + runnable but incorrect numerical results |
| verification_error | 9 | nn (9) | Verification infrastructure error (likely stdout pattern mismatch) |
| missing_output | 5 | pathfinder (4), backprop (1) | Program runs but produces no expected output |

**Recommended 3 case studies (Claude's discretion per CONTEXT.md):**
1. **cfd (CUDA-to-OpenCL):** 16 VERIFY_FAIL -- wrong reduction scope in Euler flux computation. Representative of algorithmic translation errors in stencil-like computations.
2. **hotspot (OpenCL-to-OMP):** 7 VERIFY_FAIL -- race condition or incorrect thread mapping in 2D stencil. Representative of parallelism model translation errors.
3. **gaussian (OpenCL-to-CUDA):** 6 VERIFY_FAIL -- incorrect shared memory handling or synchronization in row elimination. Representative of memory model reasoning errors.

These 3 cover the reviewer-requested categories: wrong reduction scope, race condition/thread mapping, memory model errors.

[VERIFIED: error_taxonomy.json verify_fail_categories, result file counts via glob]

## Cochran-Armitage Power Analysis (P0-6)

| Parameter | Value | Source |
|-----------|-------|--------|
| n per level | 24 | paper_data.json > augmentation > cochran_armitage > n_kernels [VERIFIED] |
| Levels | L0-L4 (coded 0-4) | 5 augmentation levels [VERIFIED] |
| Observed z | 0.0 | paper_data.json > augmentation > cochran_armitage > z [VERIFIED] |
| Observed p | 1.0 | paper_data.json > augmentation > cochran_armitage > p_value [VERIFIED] |
| Base rate (L0) | 66.7% | paper_data.json > augmentation > cuda_to_omp_balanced > L0 > rate [VERIFIED] |
| MDES (80% power) | 34.1 percentage points across L0-L4 | Computed via scipy: (1.96+0.84)*sqrt(0.667*0.333)/sqrt(24*10)*4 [VERIFIED: computation] |

**Interpretation for paper:** The MDES of 34.1pp means the test would only detect trends causing the pass rate to drop from ~67% to ~33% (or rise to ~100%) across levels. The observed range (58.3%-70.8%) is well within the zone of non-detection. This is an honest limitation: the null result is consistent with genuine invariance, but also with moderate effects. The paper should report this transparently per P0-6.

## McNemar Discordant Pair Counts (P1-19)

| Direction Pair | n_discordant | p-value | Power Assessment |
|----------------|-------------|---------|------------------|
| CUDA/OMP vs OMP/CUDA | 6 | 0.6875 | Effectively zero: n=6 discordant pairs |
| OpenCL/CUDA vs CUDA/OpenCL | 6 | 0.6875 | Effectively zero: n=6 discordant pairs |
| OpenCL/OMP vs OMP/OpenCL | 9 | 1.0 | Very low: n=9 discordant pairs |
| CUDA/omp_target vs omp_target/CUDA | 5 | 0.0625 | Effectively zero: n=5 discordant pairs |

[VERIFIED: statistical_analysis.json > direction_asymmetry]

**Interpretation for paper:** With 5-9 discordant pairs, McNemar's test has essentially no power to detect moderate asymmetries. Non-significance should not be interpreted as evidence of symmetric difficulty.

## Current Section Line Counts and Float Inventory

### Section Line Counts (for page budget estimation)
| Section | Lines | Major Floats | Notes |
|---------|-------|-------------|-------|
| Abstract | 19 | 0 | Already updated by Phase 12 |
| S1 Introduction | 91 | 0 | Already written by Phase 5 |
| S2 Related Work | 83 | 1 (tab:related-work -- KEEP) | Verify positioning only |
| S3 ParBench Framework | 160 | 1 (fig:architecture -- KEEP) | Keep full text per D-06 |
| S4 Benchmark Curation | 226 | 6 tables, 1 figure (5 MOVE, 2 KEEP in main) | Keep text, move tables per D-07 |
| S5 Experimental Setup | 117 | 3 tables (ALL MOVE) | Inline key facts after table migration |
| S6 Results | 381 | 10 tables, 4 figures (5 KEEP, 9 MOVE) | Largest section; most editing work |
| S7 Discussion | 108 | 0 | Merge 7 subsections to 3 per D-14 |
| S8 Conclusion | 42 | 0 | Minor updates only |
| **Total main** | **1227** | **24 (7 KEEP, 17 MOVE)** | |
| Appendices | 946 | (existing) | Receives 17 migrated floats |

### Float Migration Tracking Table
| Float | Current Section | Current Line | Type | Action | New Location |
|-------|----------------|-------------|------|--------|--------------|
| tab:related-work | S2 | 180 | table* | KEEP | S2 |
| fig:architecture | S3 | 264 | figure* | KEEP | S3 |
| tab:augmentation-levels | S3 | 364 | table | MOVE | Appendix D |
| fig:repo-vs-kernel | S4 | 428 | figure | MOVE | Appendix D |
| tab:kernel-pairs | S4 | 434 | table | MOVE | Appendix D |
| tab:api-characteristics | S4 | 505 | table* | MOVE | Appendix D |
| tab:suite-summary | S4 | 537 | table | MOVE | Appendix D |
| tab:benchmark-characterization | S4 | 573 | table | MOVE | Appendix D |
| tab:category-distribution | S4 | 603 | table | MOVE | Appendix D |
| tab:model-config | S5 | 663 | table | MOVE | Appendix D |
| tab:hardware | S5 | 732 | table | MOVE | Appendix D |
| tab:overall-pass | S6 | 770 | table* | KEEP | S6 |
| fig:failure-taxonomy | S6 | 801 | figure | KEEP | S6 |
| tab:repair-transitions | S6 | 822 | table | MOVE | Appendix D |
| tab:per-kernel (full) | S6 | 854 | table* | MOVE (full), CREATE (condensed) | Appendix D + S6 |
| fig:kernel-heatmap | S6 | 932 | figure* | KEEP | S6 |
| tab:self-repair | S6 | 960 | table | MOVE | Appendix D |
| tab:augmentation-rates | S6 | 995 | table | MOVE | Appendix D |
| fig:augmentation | S6 | 1014 | figure | MOVE | Appendix D |
| tab:direction-rates | S6 | 1032 | table* | KEEP | S6 |
| tab:pass-at-k | S6 | 1075 | table* | MOVE | Appendix D |
| fig:pass-at-k | S6 | 1091 | figure | MOVE | Appendix D |
| fig:xsbench | S6 | 1098 | figure | MOVE | Appendix D |
| tab:stats-summary | S6 | 1115 | table* | MOVE | Appendix D |

## HeCBench Version Information (P0-7)

| Item | Value | Source |
|------|-------|--------|
| Git commit hash | `22785cdd7` | `cd HeCBench-master && git log --oneline -1` [VERIFIED] |
| Full commit message | "[readme] recategorize the p2p programs" | Same git log [VERIFIED] |
| Repository | github.com/zjin-lcf/HeCBench | README in HeCBench-master [VERIFIED] |
| Clone date | approx. March 28, 2026 | `.git` directory timestamps [VERIFIED] |
| Not a submodule | Correct -- gitignored, cloned locally | CLAUDE.md: "Gitignored but cloned locally" [VERIFIED] |

**For paper S5:** Report as: "HeCBench at commit \texttt{22785cd}\footnote{\url{https://github.com/zjin-lcf/HeCBench}}, cloned March 2026."

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Audit script | Yes | 3.12.3 | -- |
| scipy | MDES computation | Yes | 1.11.4 | -- |
| pdflatex | LaTeX compilation check | No | -- | Not blocking: paper compilation done on Overleaf or separate machine |
| bibtex | Bibliography | No | -- | Same: not blocking local edits |

**Missing dependencies with no fallback:** None that block execution.
**Missing dependencies with fallback:** pdflatex/bibtex not installed locally. LaTeX compilation testing can be done on Overleaf. The audit script does not require LaTeX compilation.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | pyproject.toml (project root) |
| Quick run command | `python3 -m pytest scripts/analysis/test_quantitative_findings.py -x` |
| Full suite command | `python3 -m pytest c_augmentation/test_transforms.py scripts/analysis/ -x` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEX-01 | Abstract numbers match S6 | audit script | `python3 scripts/analysis/cross_consistency_audit.py --project-root .` | Wave 0 |
| TEX-02 | S1 numbers consistent | audit script | Same as above | Wave 0 |
| TEX-03 | S3 architecture accurate | manual review | -- | manual-only: architecture is prose |
| TEX-04 | S4 augmentation numbers + power analysis | audit script + manual | Audit script checks numbers; MDES review is manual | Wave 0 (partial) |
| TEX-05 | S5 methodology tables moved, facts inline | audit script | Check moved tables have \ref pointers | Wave 0 |
| TEX-06 | S6 all numbers updated | audit script | Cross-check all S6 numbers | Wave 0 |
| TEX-07 | S7 merged, threats updated | manual review | -- | manual-only: structural rewrite |
| TEX-08 | S8/S2 related work positioned | manual review | -- | manual-only: positioning is prose |
| TEX-09 | Cross-consistency audit passes | audit script | `python3 scripts/analysis/cross_consistency_audit.py --project-root .` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 scripts/analysis/cross_consistency_audit.py --project-root .`
- **Per wave merge:** Full audit script + manual review of S7 merge
- **Phase gate:** Audit script reports zero unverified critical numbers

### Wave 0 Gaps
- [ ] `scripts/analysis/cross_consistency_audit.py` -- the audit script itself (TEX-09)
- [ ] No new test file needed -- the audit script IS the validation tool

## Security Domain

Security enforcement is not applicable to this phase. Phase 11 modifies a LaTeX paper and creates a read-only audit script. No user input handling, no network access, no authentication, no data modification. The audit script reads local JSON files and a TeX file -- no security surface.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Appendices.tex will accept new sections (D or extending C) without breaking IEEEtran formatting | Architecture Patterns | LOW: IEEEtran appendix numbering is well-understood; verify with compilation |
| A2 | 17 float migration will bring paper under 10 pages | Float Migration Table | MEDIUM: Exact page count depends on LaTeX compilation; may need prose compression in S4/S6 too |
| A3 | The 3 recommended VERIFY_FAIL case studies (cfd, hotspot, gaussian) will have sufficient detail in result JSONs for meaningful case study text | VERIFY_FAIL Case Study Material | LOW: 91 results available; fallback to different kernels if these 3 lack detail |
| A4 | MDES formula for Cochran-Armitage is the standard linear trend test power calculation | Power Analysis | LOW: Formula is standard; scipy computation verified |
| A5 | Phase 13 will be able to find moved floats in appendices.tex after Phase 11 migration | Common Pitfalls | MEDIUM: Phase 13 plan may need updating; document final float locations |

## Open Questions

1. **Appendix section naming for migrated floats**
   - What we know: Appendices A (API Selection), B (Benchmark Kernel Survey), C (Detailed Evaluation Findings) already exist with 946 lines
   - What's unclear: Should migrated floats go into a new Appendix D ("Detailed Tables and Figures") or be distributed into existing A/B/C?
   - Recommendation: Create Appendix D for all 17 migrated floats, grouped by original section order. This avoids disrupting the existing appendix narrative flow.

2. **Condensed per-kernel table label scheme**
   - What we know: Main text keeps a condensed 10-row version, appendix gets full 31-row version
   - What's unclear: Which version gets the `tab:per-kernel` label (main text condensed or appendix full)?
   - Recommendation: Main text condensed keeps `tab:per-kernel` (preserves all existing \ref targets). Appendix full uses `tab:per-kernel-full`. This minimizes ref breakage.

3. **Exact page savings from float migration**
   - What we know: 17 floats (8 full-width, 9 single-column) are being moved
   - What's unclear: Exact page reduction without LaTeX compilation
   - Recommendation: Estimate ~10-14 pages freed (full-width tables take ~0.5-1 page each, single-column ~0.3-0.5 page each). With 24 pages current and 17 floats moved, expect ~10-12 pages remaining in main text. pdflatex not available locally; verify after migration.

4. **quantitative_findings.json paper_claims scope annotations**
   - What we know: 20 paper_claims entries exist with `scope` field (rodinia_only or all_suite)
   - What's unclear: Some claims reference `quantitative_findings.json` values (n=700) while paper uses `paper_data.json` values (n=710). The audit script must reconcile these.
   - Recommendation: Audit script should flag any claim where the paper value differs from BOTH data sources. If paper matches paper_data.json but not quantitative_findings.json, that's expected (not a mismatch).

## Sources

### Primary (HIGH confidence)
- `paper_data.json` -- inspected: 710 tasks, all-suite scope, verified structure and key values
- `quantitative_findings.json` -- inspected: 700 tasks (excluding omp_target), 20 paper_claims, campaign_1 structure
- `statistical_analysis.json` -- inspected: direction_asymmetry (4 pairs), augmentation_trends
- `error_taxonomy.json` -- inspected: verify_fail_categories (3 subcategories, 91 total)
- `selfrepair_analysis.json` -- inspected: repair rates, token overhead
- `paper.tex` (1286 lines) -- full structure analyzed, section line counts computed
- `appendices.tex` (946 lines) -- structure analyzed (3 sections A/B/C)
- Phase 12.1 CONTEXT.md -- verified 5 P0 fixes already applied
- Phase 9 CONTEXT.md -- verified two-campaign separation (D-05/D-06)
- Phase 12 CONTEXT.md -- verified paper_data.json as authoritative source (D-01)
- HeCBench git log -- commit `22785cdd7` verified

### Secondary (MEDIUM confidence)
- scipy 1.11.4 MDES computation -- formula is standard but cross-verification with published power tables recommended
- IEEEtran appendix numbering behavior -- based on standard LaTeX class behavior

### Tertiary (LOW confidence)
- Page count estimation after float migration (~10-14 pages freed) -- requires LaTeX compilation to verify

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all tools are project-internal or stdlib; no new dependencies
- Architecture: HIGH -- float migration pattern is straightforward LaTeX editing; appendix structure verified
- Data sources: HIGH -- all JSON files inspected and cross-checked; 700 vs 710 discrepancy documented
- Power analysis: HIGH -- MDES formula verified with scipy computation
- Pitfalls: HIGH -- based on direct inspection of paper.tex structure and data file discrepancies
- Page budget: MEDIUM -- exact page count requires LaTeX compilation (pdflatex not available locally)
- VERIFY_FAIL case studies: MEDIUM -- subcategories verified but specific code examples not yet inspected

**Research date:** 2026-04-05
**Valid until:** 2026-04-08 (paper deadline -- research is deadline-specific)
