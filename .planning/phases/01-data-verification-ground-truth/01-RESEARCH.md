# Phase 1: Data Verification & Ground Truth - Research

**Researched:** 2026-04-03
**Domain:** LaTeX paper data verification against raw evaluation result JSONs
**Confidence:** HIGH

## Summary

Phase 1 requires cross-checking every numerical claim, table cell, and data-backed prose statement in Sections 1-6 of `paper.tex` against ground truth data files on disk, then fixing discrepancies inline and regenerating all analysis files and figures. The paper is a 1035-line IEEE double-column LaTeX document with 7 main-body figures, 12 data tables, and approximately 50+ distinct numerical claims across Sections 1-5 (the verification scope).

The primary ground truth source is raw result JSONs in `results/evaluation/together-qwen-3.5-397b-a17b/` (1248 files on disk). The derived analysis file `paper_data.json` (generated April 1, 08:11 UTC) was generated from a subset of these files and is internally consistent with the paper's primary campaign numbers (480 tasks, 18 Rodinia kernels). However, 230 new result files have appeared since paper_data.json was generated (from ongoing tmux sessions), making regeneration necessary at phase end. A separate `statistical_analysis.json` covers a broader scope (906 records including pass@k and hecbench) and has **different McNemar values** than what appears in the paper -- the paper correctly uses paper_data.json's L0 Rodinia-only values, not the broader statistical_analysis.json values.

**Primary recommendation:** Verify section-by-section (S1 through S5, then S6 Qwen data), using raw result JSONs as primary source and paper_data.json as secondary, fixing inline. Regenerate all analysis files and figures at the end using the established scripts with the venv activated.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Fix discrepancies inline in paper.tex immediately during verification -- no separate discrepancy report. The git diff serves as the audit trail.
- **D-02:** Add brief LaTeX source comments next to key data-derived numbers noting the source file and field (e.g., `% src: paper_data.json > overall_pass_rate`). Helps future edits stay grounded.
- **D-03:** Fix table structure too (not just data values) when the data clearly demands it (e.g., missing API column, wrong row order). Don't defer structural fixes to downstream phases.
- **D-04:** Verify explicit numbers, table cells, AND qualitative prose claims backed by data (e.g., "CUDA-to-OMP is the easiest direction" must match direction pass rates). Not just numbers and tables.
- **D-05:** Verify Qwen data in Section 5 (Results) too -- Qwen Rodinia data is complete and frozen. GPT-4.1 mini placeholders are out of scope (no data yet).
- **D-06:** Also regenerate figures using generate_paper_figures.py -- verify figure output matches current data. Tables + figures + inline numbers + data-backed prose are all in scope.
- **D-07:** Ground truth source is raw result JSONs in `results/evaluation/together-qwen-*/`, NOT derived analysis files (paper_data.json etc.). Raw files are the primary source; derived files may be stale or have aggregation bugs.
- **D-08:** Verify against raw result JSONs first (primary source of truth). Regenerate all analysis files (paper_data.json, statistical_analysis.json, selfrepair_analysis.json) and figures at the END of Phase 1, so downstream phases have fresh data.
- **D-09:** Full regeneration scope at end: all analysis scripts + figure generation (generate_paper_figures.py). Downstream phases (2-5) start with completely fresh data and figures.
- **D-10:** Data freeze at Phase 1 start. Count result files once at the beginning, verify against that count. New results from running tmux sessions (qwen_hecbench, qwen_small) are out of scope -- they get picked up in a future re-run.

### Claude's Discretion
- Verification ordering within sections (top-to-bottom, table-by-table, or claim-by-claim)
- Whether to batch-verify all tables first vs. verify section-by-section
- Exact format of LaTeX source comments (as long as they identify source file + field)
- How to handle GPT-4.1 mini references encountered during verification (skip silently or note for future)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VERIFY-01 | Every numerical claim in Sections 1-5 cross-checked against ground truth JSON files | Paper-to-data mapping documented below; 50+ claims identified across abstract, S1, S2, S3, S4, S5 |
| VERIFY-02 | Suite-summary table (tab:suite-summary) verified: kernel count, spec count, API counts match manifest.jsonl + specs/ on disk | Manifest has 211 entries (5 phantom), 206 spec files on disk; paper claims 96 curated = 60+25+4+4+3; all verified correct |
| VERIFY-03 | Augmentation level definitions table (tab:augmentation-levels) verified against LEVEL_FRACTIONS in c_augmentation/augment_dataset.py | LEVEL_FRACTIONS = {1: 0.0, 2: 0.33, 3: 0.66, 4: 1.0}; paper table values match code |
| VERIFY-04 | Model config table (tab:model-config) coherent post-C1 swap: Qwen + GPT-4.1 mini descriptions accurate, no Gemini remnants | Paper already has Qwen + GPT-4.1 mini; must grep for any remaining Gemini references |
| VERIFY-05 | Hardware/software table (tab:hardware) verified against actual system | Verified: nvcc 12.3, GCC 12.4.0, RTX 4070, Ryzen 9 7900X, Ubuntu 24.04, Python 3.12.3 -- all match paper |
| VERIFY-06 | Analysis files freshness assessed: paper_data.json checked for coverage; re-run if stale | paper_data.json from April 1 covers 1018 files; 230 new files since then; regeneration required at end |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `python3` always, never `python`. Venv: `source env_parbench/bin/activate`
- Result JSONs are immutable -- never modify existing result files
- `manifest.jsonl` is append-only -- never modify existing entries
- Running tmux sessions (qwen_hecbench, qwen_small) MUST NOT be touched
- Use `overall_status` (not `run_status`) as the authoritative verdict in result JSONs
- `or {}` guard for nullable JSON fields
- Ruff runs automatically via PostToolUse hook on `.py` edits
- `/validate` before every commit; pre-commit hook enforces sentinel
- Global flags BEFORE subcommand in harness CLI
- NEVER touch CUDA/OMP results (inviolable protection)
- NEVER touch Qwen results (inviolable protection)

## Standard Stack

This phase is primarily a manual verification task (reading LaTeX, cross-referencing JSON data). No new libraries are needed. The existing scripts are the "stack":

### Core Tools
| Script | Purpose | Invocation |
|--------|---------|------------|
| `scripts/analysis/generate_paper_data.py` | Regenerate paper_data.json from raw results | `python3 scripts/analysis/generate_paper_data.py --results-dir results/evaluation/together-qwen-3.5-397b-a17b --output results/analysis/paper_data.json -v` |
| `scripts/analysis/statistical_analysis.py` | Regenerate statistical_analysis.json | `python3 scripts/analysis/statistical_analysis.py --project-root /home/samyak/Desktop/parbench_sam -v` |
| `scripts/analysis/selfrepair_analysis.py` | Regenerate selfrepair_analysis.json | `python3 scripts/analysis/selfrepair_analysis.py --project-root /home/samyak/Desktop/parbench_sam` |
| `scripts/generate_paper_figures.py` | Regenerate all paper figures (F2-F7, C.1-C.4, T2) | `python3 scripts/generate_paper_figures.py --project-root /home/samyak/Desktop/parbench_sam --figure all --output-dir docs/paper/figures/` |

### Supporting Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| `jq` / `python3 -c` | Ad-hoc JSON queries | For spot-checking individual values against raw result JSONs |
| `grep` / `Grep` tool | LaTeX claim extraction | Find all numerical claims in paper.tex |
| `wc -l`, `ls` | File counting | Verify spec counts, manifest entries |

**Venv activation required:** `source env_parbench/bin/activate` before running any script. The `scienceplots` dependency is only available in the venv.

## Architecture Patterns

### Verification Flow Pattern

```
For each section (S1 through S6):
  1. Extract all numerical claims from LaTeX
  2. For each claim:
     a. Identify ground truth source (raw JSON > paper_data.json > code)
     b. Compare claim vs. ground truth
     c. If mismatch: fix inline in paper.tex + add source comment
     d. If match: add source comment if not present
  3. Verify qualitative prose claims against data
  
After all sections verified:
  4. Regenerate all analysis files (scripts)
  5. Regenerate all figures
  6. Final cross-check: re-verify key numbers against fresh files
```

### Data Source Hierarchy

```
Priority 1: Raw result JSONs in results/evaluation/together-qwen-3.5-397b-a17b/
  - 1248 files on disk (as of data freeze)
  - Each file has overall_status, attempts[], build/run/verify details
  - Authority for: per-task outcomes, attempt counts, error types

Priority 2: paper_data.json (derived, April 1)
  - Consolidated view of 480 primary + 426 pass@k tasks
  - Authority for: aggregate rates, CIs, Cochran-Armitage, McNemar, self-repair
  - Contains PRIMARY CAMPAIGN data (18 Rodinia kernels only)

Priority 3: statistical_analysis.json (derived, March 31)  
  - Covers ALL 906 tasks (broader scope than paper's primary campaign)
  - CAUTION: McNemar values differ from paper (uses all data, not L0-only)
  - Authority for: broader statistical tests only

Priority 4: Code itself
  - c_augmentation/augment_dataset.py: LEVEL_FRACTIONS dictionary
  - manifest.jsonl: kernel registry
  - specs/*.json: spec details
```

### LaTeX Source Comment Convention

```latex
% src: paper_data.json > primary_campaign > overall > pass_rate
Qwen~3.5 achieves 36.2\% overall...

% src: paper_data.json > primary_campaign > by_direction > cuda-to-omp > pass_rate  
65.0\% [54.1\%, 74.6\%]...

% src: LEVEL_FRACTIONS in c_augmentation/augment_dataset.py
```

### Recommended Project Structure
```
docs/paper/latex/paper.tex       # The file being verified and fixed
results/analysis/                # Analysis files to regenerate at end
  paper_data.json                # Primary derived data (regenerated)
  statistical_analysis.json      # Statistical tests (regenerated)
  selfrepair_analysis.json       # Self-repair analysis (regenerated)
  error_taxonomy.json            # Error taxonomy (regenerated)
  sloc_analysis.json             # SLoC data (regenerated)
docs/paper/figures/              # Figures to regenerate at end
  f2_repo_vs_kernel.pdf          # Figure 2
  f3_kernel_model_heatmap.pdf    # Figure 3
  f4_failure_taxonomy.pdf        # Figure 4
  f5_pass_at_k_by_direction.pdf  # Figure 5
  f6_xsbench_comparison.pdf      # Figure 6
  f7_augmentation_robustness.pdf # Figure 7
  c1-c4, t2                     # Appendix + table
```

### Anti-Patterns to Avoid
- **Modifying result JSONs:** Results are immutable. Fix the paper, not the data.
- **Using statistical_analysis.json for McNemar claims:** The paper's McNemar values come from paper_data.json (L0 Rodinia-only scope), not statistical_analysis.json (broader scope). Do not "fix" the paper to match the wrong JSON.
- **Trusting derived files without cross-checking raw:** D-07 mandates raw JSONs as primary source. Spot-check paper_data.json aggregation against raw files before trusting it.
- **Regenerating before verifying:** D-08 mandates verify first, regenerate at the END. Regenerating early could mask stale data that the paper still references.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wilson confidence intervals | Manual CI calculation | `paper_data.json` values or `statistical_analysis.py` | Wilson formula implementation already correct in scripts |
| Cochran-Armitage test | Manual z-score computation | `paper_data.json > cochran_armitage` field | Already computed with correct L0 Rodinia-only scope |
| McNemar tests | Manual contingency table analysis | `paper_data.json > direction_asymmetry` field | Already computed with correct L0 paired kernel scope |
| pass@k estimates | Manual comb() calculation | `paper_data.json > passk_campaign` field | Chen et al. formula implemented in generate_paper_data.py |
| Figure regeneration | Manual matplotlib scripts | `generate_paper_figures.py --figure all` | Unified script with Okabe-Ito palette, scienceplots |

## Common Pitfalls

### Pitfall 1: Statistical Analysis Scope Mismatch
**What goes wrong:** Using statistical_analysis.json McNemar values in the paper when the paper's McNemar tests are scoped to L0 Rodinia-only pairs.
**Why it happens:** statistical_analysis.json covers all 906 tasks; paper_data.json covers only the 480 primary campaign. McNemar paired n values differ: JSON has n=24/20/18, paper has n=16/17/15.
**How to avoid:** Always use paper_data.json for paper numbers. statistical_analysis.json is for broader analysis only.
**Warning signs:** n_paired values don't match what's in the paper.

### Pitfall 2: Stale File Count After Data Freeze
**What goes wrong:** New result files from running tmux sessions accumulate during Phase 1, causing file counts to drift.
**Why it happens:** qwen_hecbench and qwen_small tmux sessions are actively writing new files.
**How to avoid:** D-10 mandates data freeze at start. Count files once (1248 as of research), verify against that count throughout. New files are out of scope.
**Warning signs:** `ls results/evaluation/together-qwen-*/ | wc -l` returns a number different from 1248.

### Pitfall 3: Phantom Manifest Entries
**What goes wrong:** Counting manifest entries (211) and concluding there's a discrepancy with spec files (206).
**Why it happens:** 5 deleted phantom Rodinia specs still in manifest.jsonl (append-only invariant).
**How to avoid:** Paper says 96 curated specs, not 206 total. The 96 = 60 Rodinia + 25 HeCBench curated + 4 XSBench + 4 RSBench + 3 mixbench.
**Warning signs:** Manifest count != spec file count.

### Pitfall 4: Self-Repair Analysis File Scope
**What goes wrong:** selfrepair_analysis.json total_results=1018 includes all files (hecbench, pass@k with multiple samples), while the paper references 480 primary campaign tasks.
**Why it happens:** selfrepair_analysis.py processes all result files, not just primary campaign.
**How to avoid:** Use paper_data.json > self_repair section for paper numbers (scoped to 480 primary tasks).
**Warning signs:** Self-repair total doesn't match 480.

### Pitfall 5: Regeneration Order Matters
**What goes wrong:** Regenerating figures before regenerating paper_data.json, producing figures based on stale data.
**Why it happens:** generate_paper_figures.py reads from paper_data.json and raw results.
**How to avoid:** Regeneration order: (1) generate_paper_data.py, (2) statistical_analysis.py, (3) selfrepair_analysis.py, (4) generate_paper_figures.py.
**Warning signs:** Figure data doesn't match freshly regenerated JSON.

### Pitfall 6: Percent vs Fraction Confusion
**What goes wrong:** Paper uses percentages (36.2%) but JSONs store fractions (0.3625).
**Why it happens:** Natural mismatch between display format and storage format.
**How to avoid:** Always convert: fraction * 100 = percent. Round to 1 decimal for paper display.
**Warning signs:** Values off by factor of 100, or rounding disagreement (36.25 vs 36.2 vs 36.3).

## Code Examples

### Spot-checking a claim against raw result JSONs
```python
# Verify: "174 PASS out of 480 primary tasks"
import json
from pathlib import Path
from collections import Counter

result_dir = Path('results/evaluation/together-qwen-3.5-397b-a17b')
files = sorted(result_dir.glob('*.json'))

# Filter to primary campaign (temp=0.0, not pass@k samples)
primary = [f for f in files if not any(
    s in f.name for s in ['-s0.json', '-s1.json', '-s2.json']
)]

# Filter to Rodinia only (primary campaign is 18 Rodinia kernels)
rodinia_primary = [f for f in primary if 'rodinia-' in f.name]

# Exclude KNOWN_FAIL source specs
known_fail = {'kmeans-cuda', 'mummergpu-cuda', 'mummergpu-omp', 
              'hybridsort-cuda', 'nn-opencl', 'kmeans-opencl'}

statuses = Counter()
for f in rodinia_primary:
    data = json.loads(f.read_text())
    # Check if source spec is known_fail
    src_id = data.get('source_spec_id', '')
    if any(kf in src_id for kf in known_fail):
        continue
    status = data.get('overall_status', 'UNKNOWN')
    statuses[status] += 1

print(f"Total tasks: {sum(statuses.values())}")
print(f"PASS: {statuses.get('PASS', 0)}")
print(f"BUILD_FAIL: {statuses.get('BUILD_FAIL', 0)}")
```

### Verifying augmentation level table against code
```python
# Verify: Table tab:augmentation-levels matches LEVEL_FRACTIONS
# Paper says: L1=1 site, L2=33%, L3=66%, L4=100%
# Code says:  LEVEL_FRACTIONS = {1: 0.0, 2: 0.33, 3: 0.66, 4: 1.0}
# L1: fraction=0.0 -> max(1, floor(n*0.0)) = 1 (matches "1 site per transform")
# L2: fraction=0.33 -> max(1, floor(n*0.33)) (matches "33% of candidates")
# L3: fraction=0.66 -> max(1, floor(n*0.66)) (matches "66% of candidates")
# L4: fraction=1.0 -> all candidates (matches "100% of candidates")
```

### Adding a LaTeX source comment
```latex
% src: paper_data.json > primary_campaign > overall > pass_rate (= 0.3625)
Qwen~3.5 397B-A17B achieves an overall pass rate of 36.2\%
% src: paper_data.json > primary_campaign > overall > ci_lower, ci_upper
[32.1\%, 40.6\%]
```

## Key Data Points Pre-Verified During Research

These were verified during research and can be referenced directly by the planner:

### Verified CORRECT (paper matches ground truth)
| Claim Location | Paper Value | Ground Truth Source | Match? |
|---------------|-------------|---------------------|--------|
| Abstract: overall pass rate | 36.2% [32.1%, 40.6%] | paper_data.json > primary_campaign > overall | YES |
| Abstract: BUILD_FAIL % | 30.8% | 148/480 = 30.83% | YES |
| Abstract: VERIFY_FAIL % | 9.8% | 47/480 = 9.79% | YES |
| S1: CUDA-to-OMP L0 | 68.8% | 11/16 = 68.75% | YES |
| S1: CUDA-to-OMP all levels | 65.0% [54.1%, 74.6%] | paper_data.json > by_direction > cuda-to-omp | YES |
| S1: Cochran-Armitage | z=-0.17, p=0.87 | paper_data.json > cochran_armitage: z=-0.1657, p=0.868 | YES (rounded) |
| S1: Self-repair 17.5% to 36.2% | 84/480 to 174/480 | paper_data.json > self_repair | YES |
| S1: 90 repaired, 5 regressions | 90, 5 | paper_data.json > self_repair | YES |
| S3: 96 specs, 5 suites | 60+25+4+4+3=96 | spec files on disk | YES |
| S4: tab:suite-summary totals | 35 kernels, 96 total, 88 PASS, 8 KF | spec files + known-issues.md | YES |
| S4: 206 total spec files | 206 | `ls specs/*.json | wc -l` | YES |
| S5: tab:augmentation-levels fractions | L1=1, L2=33%, L3=66%, L4=100% | LEVEL_FRACTIONS in code | YES |
| S5: Hardware table (Qwen column) | RTX 4070, Ryzen 9 7900X, Ubuntu 24.04, HPC SDK 24.3, GCC 12.4, Python 3.12.3 | nvcc/gcc/nvidia-smi/uname output | YES |
| S6: Per-kernel table row counts | 18 kernels, totals sum to 480 | paper_data.json > by_kernel | YES |
| S6: McNemar p-values | 0.625, 0.688, 0.727 | paper_data.json > direction_asymmetry | YES |
| S6: McNemar paired n | 16, 17, 15 | paper_data.json > direction_asymmetry > n_paired | YES |
| S6: Cochran-Armitage pass counts | 11,10,11,9,11 | paper_data.json > cochran_armitage > pass_counts | YES |

### Potential Issues Found During Research
| Issue | Details | Severity |
|-------|---------|----------|
| paper_data.json staleness | Generated April 1, 230 new result files since. Regeneration needed at end. | MEDIUM (end-of-phase task) |
| statistical_analysis.json scope mismatch | Covers 906 tasks including hecbench and pass@k. Paper's McNemar uses L0-only from paper_data.json. These are NOT the same. | HIGH (avoid using wrong source) |
| selfrepair_analysis.json scope mismatch | Covers 1018 files. Paper uses 480 primary tasks. | HIGH (use paper_data.json) |
| S6: Failure taxonomy percentages | Paper says 148/306=48.4% of failures. Research confirms 306 failures (480-174=306), 148/306=48.37%. | NONE (matches) |
| Bonferroni correction | Paper uses alpha=0.0167 (3 tests). statistical_analysis.json uses alpha=0.0125 (4 tests including omp_target). Paper is correct for primary scope. | LOW (paper correct, JSON different scope) |
| KNOWN_FAIL count | Paper says 8 (6 Rodinia + 2 HeCBench). known-issues.md lists exactly 8. | NONE (matches) |
| Gemini remnants (VERIFY-04) | Need to grep for "Gemini", "gemini", "flash", "Flash Lite" in paper.tex | NOT YET CHECKED (planner task) |

## State of the Art

Not applicable -- this is a data verification phase, not a technology adoption phase.

## Open Questions

1. **Gemini remnant check not yet performed**
   - What we know: Paper was rewritten from a 3-model (Claude+Gemini+Groq) to 2-model (Qwen+GPT-4.1) framing
   - What's unclear: Whether any Gemini-specific text remains beyond the `\pending{}` macros
   - Recommendation: `grep -in "gemini\|flash.lite\|groq\|llama\|claude" docs/paper/latex/paper.tex` as first task

2. **Pass@k campaign file count discrepancy**
   - What we know: paper_data.json says 426 pass@k tasks. On disk, 468 sample files exist (some may be hecbench/non-Rodinia).
   - What's unclear: Whether the 468 includes non-Rodinia pass@k samples
   - Recommendation: Verify by counting rodinia-only pass@k files with -s0/-s1/-s2 suffixes

3. **SLoC data for tab:benchmark-characterization**
   - What we know: sloc_analysis.json covers 18 kernels. Paper table has 35 kernels with SLoC ranges.
   - What's unclear: Whether the paper's SLoC values for non-Rodinia kernels are independently sourced or from sloc_analysis.json
   - Recommendation: Verify SLoC values in tab:benchmark-characterization against sloc_analysis.json and/or direct wc -l counts

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `pyproject.toml` (pytest section) |
| Quick run command | `source env_parbench/bin/activate && python3 -m pytest scripts/analysis/test_generate_paper_data.py -x -q` |
| Full suite command | `source env_parbench/bin/activate && python3 -m pytest scripts/analysis/test_generate_paper_data.py scripts/analysis/test_statistical_analysis.py scripts/analysis/test_build_error_taxonomy.py -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VERIFY-01 | Numerical claims match ground truth | manual + smoke | `python3 -m pytest scripts/analysis/test_generate_paper_data.py -x` | YES (20 tests) |
| VERIFY-02 | Suite-summary table matches manifest+specs | manual | `python3 -c "..."` (inline count check) | Manual only |
| VERIFY-03 | Augmentation levels match LEVEL_FRACTIONS | manual | `grep LEVEL_FRACTIONS c_augmentation/augment_dataset.py` | Manual only |
| VERIFY-04 | No Gemini remnants, model table accurate | manual | `grep -in gemini docs/paper/latex/paper.tex` | Manual only |
| VERIFY-05 | Hardware table matches actual system | manual | `nvcc --version && gcc --version && nvidia-smi` | Manual only |
| VERIFY-06 | Analysis files regenerated fresh | smoke | Run all 4 scripts, then re-run test suite | YES |

### Sampling Rate
- **Per task commit:** `python3 -m pytest scripts/analysis/test_generate_paper_data.py -x -q`
- **Per wave merge:** Full analysis test suite
- **Phase gate:** All analysis tests green + regenerated files committed

### Wave 0 Gaps
None -- existing test infrastructure covers paper_data.json validation with 20 tests. No new test files needed for this phase. Manual verification is the primary method.

## Sources

### Primary (HIGH confidence)
- Raw result JSONs: `results/evaluation/together-qwen-3.5-397b-a17b/` (1248 files, examined directly)
- `results/analysis/paper_data.json` (read and cross-checked against raw data)
- `results/analysis/statistical_analysis.json` (read, scope difference documented)
- `results/analysis/selfrepair_analysis.json` (read, scope difference documented)
- `c_augmentation/augment_dataset.py` line 111: `LEVEL_FRACTIONS = {1: 0.0, 2: 0.33, 3: 0.66, 4: 1.0}`
- `manifest.jsonl` (211 entries, 5 phantom, verified)
- `specs/` directory (206 files, verified)
- System commands: `nvcc --version`, `gcc --version`, `nvidia-smi`, `uname -r`, `python3 --version`
- `docs/paper/latex/paper.tex` (1035 lines, all sections read)

### Secondary (MEDIUM confidence)
- `config/compiler_inventory.txt` (captured versions, cross-checked against live system -- matches)
- Analysis script help text (verified CLI interfaces for all 4 regeneration scripts)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools are existing project scripts, verified working
- Architecture: HIGH - Verification flow is straightforward; data hierarchy is clear from direct investigation
- Pitfalls: HIGH - Multiple pitfalls discovered through direct data investigation (scope mismatch between JSON files is the most critical)

**Research date:** 2026-04-03
**Valid until:** 2026-04-08 (paper submission deadline; data is frozen)
