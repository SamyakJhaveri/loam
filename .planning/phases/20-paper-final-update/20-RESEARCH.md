# Phase 20: paper-final-update - Research

**Researched:** 2026-04-08
**Domain:** LaTeX paper editing, data-driven numeric updates, analysis pipeline re-execution
**Confidence:** HIGH

## Summary

Phase 20 is a paper-update phase that replaces all stale GPT-4.1-mini numbers in three LaTeX files (`overleaf.tex`, `paper.tex`, `appendices.tex`) with freshly generated values from the Phase 19 analysis pipeline. The scope is well-defined: 13 structural changes documented in `19-STRUCTURAL-CHANGES.md`, numeric replacements throughout the body, and a mandatory re-run of the analysis pipeline (Task 0) because the user has added 32 new XSBench GPT result files since Phase 19 ran.

The three files have different structures: `overleaf.tex` (1,360 lines, the SC26 submission artifact) and `paper.tex` (1,282 lines, sync copy) share body content but have different preambles, different section ordering (Related Work is Section 2 in paper.tex vs Section 7 in overleaf.tex), and different methodology subsection text. The `appendices.tex` (1,434 lines) is shared by both via `\input{}` and needs only numeric updates in three tables plus one stats summary row. Both `overleaf.tex` and `paper.tex` already have identical methodology working-tree edits (pending rewrite, GPT machine specs, generalizability paragraph, ParaCodex text); these need to be folded into the Phase 20 commit.

**Primary recommendation:** Execute as a sequential pipeline: (1) stage XSBench files, (2) re-run all 4 analysis scripts, (3) capture fresh numbers to 20-NUMBERS.md, (4) edit overleaf.tex (all 13 structural changes + numeric), (5) edit appendices.tex (3 tables + stats row), (6) edit paper.tex (mirror numeric changes, different line numbers), (7) spot-check 10+ numbers, (8) validate and commit.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** `overleaf.tex` is the SC26 submission artifact (primary). It gets top priority for correctness.
- **D-02:** `paper.tex` must be kept in sync with `overleaf.tex` -- apply both the methodology text edits AND the GPT numeric updates to paper.tex.
- **D-03:** `appendices.tex` is shared between both files; update it once.
- **D-04:** Update numbers in-place AND revise interpretive prose where the story was inverted by the new data.
- **D-05:** Follow `19-STRUCTURAL-CHANGES.md` exactly for all 13 listed items.
- **D-06:** User will find and add valid XSBench GPT result files before Phase 20 executes.
- **D-07:** After XSBench files are added, Phase 20 Task 0 re-runs the full Phase 19 analysis pipeline (all scripts).
- **D-08:** After re-run, if XSBench GPT coverage is still significantly less than Qwen coverage, add a brief qualification sentence.
- **D-09:** The methodology text edits already in `overleaf.tex` working tree are correct and intentional. DO NOT discard them.
- **D-10:** Fold these methodology edits into the single Phase 20 commit.
- **D-11:** Apply the same methodology text edits to `paper.tex` as part of Phase 20 execution.
- **D-12:** Create `20-02-PLAN.md` as the fresh execution plan. `20-01-PLAN.md` is preserved as reference.
- **D-13:** Standard `/validate` (4-wave protocol) required before commit.
- **D-14:** After commit: try `pdflatex -interaction=nonstopmode overleaf.tex` and check for errors.

### Claude's Discretion
- Error taxonomy subcategory counts in failure taxonomy prose: update from `error_taxonomy.json` after re-run.
- Wilson CI recalculation for the Aggregate row in Table 3: compute from new combined counts.
- Exact per-direction rates for cross-model direction table: read from freshly generated JSON.

### Deferred Ideas (OUT OF SCOPE)
- XSBench GPT eval re-run (full campaign) -- post-submission work.
- Page budget compression -- deferred to manual edit.
- Per-kernel agreement matrix heatmap figure.
- Cross-model pass@k comparison.
</user_constraints>

## Current State of LaTeX Files

### File Sizes and Structure [VERIFIED: disk]
| File | Lines | Role | Working Tree Changes |
|------|-------|------|---------------------|
| `overleaf.tex` | 1,360 | PRIMARY submission artifact | +11/-5 (methodology edits) |
| `paper.tex` | 1,282 | Sync copy | +11/-5 (same methodology edits) |
| `appendices.tex` | 1,434 | Shared appendix tables | +16/-16 (hardware table, pending cmd) |

### Working Tree Edits Already Present [VERIFIED: git diff]

Both `overleaf.tex` and `paper.tex` have IDENTICAL working tree edits that must be preserved (not discarded):

1. **`\pending{}` command rewrite** (line ~45/36): Changed from red PENDING-GPT marker to italic "Provided in Artifact Description appendix"
2. **GPT collaborator machine specs** (line ~634/647): Replaced `\pending{GPU model...}` with actual ALCF Polaris specs (A100 GPU, EPYC 7543P CPU)
3. **Generalizability paragraph** (line ~1217/1229): New paragraph in Discussion > Threats to Validity section
4. **ParaCodex text** (line ~1295/254): Simplified from "companion system from our research group" to "profiling-guided autonomous coding agent"
5. **TODO comment cleanup** (line ~667/679): Removed `(samyak)` from TODO comment

`appendices.tex` working tree edits:
1. **Model table** (line ~1057): `\pending{size}` replaced with `N/D`
2. **Hardware table** (lines ~1069-1081): All 7 GPT column `\pending{}` markers replaced with actual values or `---`

**CRITICAL:** All working tree edits in all three files must be preserved and committed as part of Phase 20. The `paper.tex` methodology edits are ALREADY applied; no propagation needed from overleaf.tex to paper.tex for these specific changes.

### Preamble Differences [VERIFIED: diff comparison]

The two main files have significantly different preambles:
- **overleaf.tex**: `\documentclass` on line 1, custom JSON lstlisting language with colored literals, `\usepackage{float}`, `\usepackage{cuted}`, title/authors defined after packages
- **paper.tex**: `\documentclass` on line 5 (after comments), simpler `\lstset{}`, title/authors on line ~52, no `\usepackage{float}`
- **Status command casing**: overleaf uses `\textsc{BUILD\_FAIL}`, paper uses `\textsc{Build\_Fail}` -- these differ and MUST NOT be unified

### Section Ordering Differences [VERIFIED: grep]

| Section | overleaf.tex Line | paper.tex Line |
|---------|------------------|----------------|
| Abstract | 125 | 81 |
| Introduction | 146 | 92 |
| Related Work | **1227** | **189** |
| ParBench Framework | 251 | 276 |
| Benchmark Curation | 404 | 417 |
| Experimental Setup | 538 | 551 |
| Results | 671 | 684 |
| Discussion | 1147 | 1160 |
| Conclusion | 1318 | 1239 |

**CRITICAL:** Section 6 (Results) and its subsections have a consistent ~13-line offset between the two files. However, Related Work is in completely different positions. When applying numeric edits, ALWAYS grep for the exact anchor text rather than using line numbers.

### Methodology Section Structural Differences [VERIFIED: diff]

The Framework section (Section 2/3) has DIFFERENT subsection ordering AND different text between the two files:
- **overleaf.tex order**: Spec Schema -> Evaluation Pipeline -> Augmentation Engine -> Harness Pipeline
- **paper.tex order**: Spec Schema -> Harness Pipeline -> Augmentation Engine -> Evaluation Pipeline

The text content also differs (overleaf has more detailed descriptions, different figure reference conventions). **DO NOT attempt to synchronize these sections** -- they diverged intentionally. Phase 20 only edits numeric/GPT content, not methodology prose.

## Analysis Pipeline Re-Run (Task 0)

### XSBench GPT File Status [VERIFIED: disk + git ls-files]

| Metric | Value |
|--------|-------|
| XSBench GPT files on disk | 38 |
| XSBench GPT files committed | 6 (omp-to-cuda + opencl-to-cuda self-repair only) |
| XSBench GPT files untracked | 32 |
| XSBench GPT directions covered | 6 (cuda-to-omp, cuda-to-opencl, omp-to-cuda, omp-to-opencl, opencl-to-cuda, opencl-to-omp) |
| Total GPT eval files on disk | 942 (was 910 at Phase 19) |

**IMPORTANT:** The 19-STRUCTURAL-CHANGES.md was generated with 910 files (557 primary tasks). After adding 32 XSBench files, the numbers WILL change. Every number from 19-STRUCTURAL-CHANGES.md must be re-verified against freshly generated JSONs. Do NOT blindly copy numbers from 19-STRUCTURAL-CHANGES.md.

### Exact CLI Invocations [VERIFIED: --help output of each script]

All scripts must be run from the project root with the venv activated:

```bash
source env_parbench/bin/activate

# 1. Regenerate eval_summary.json (aggregates all result files)
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  -v

# 2. Regenerate paper_data_gpt41mini.json (GPT primary campaign stats)
python3 scripts/analysis/generate_paper_data.py \
  --results-dir results/evaluation/azure-gpt-4.1-mini \
  --output results/analysis/paper_data_gpt41mini.json \
  -v

# 3. Regenerate cross_model_comparison.json
python3 scripts/analysis/cross_model_comparison.py \
  --qwen-data results/analysis/paper_data.json \
  --gpt-data results/analysis/paper_data_gpt41mini.json \
  --output results/analysis/cross_model_comparison.json \
  -v

# 4. Regenerate error_taxonomy.json
python3 scripts/analysis/build_error_taxonomy.py \
  --project-root /home/samyak/Desktop/parbench_sam

# 5. Regenerate figures (MAY FAIL -- scienceplots available in venv but pdflatex is not)
python3 scripts/generate_paper_figures.py --figure all
```

**Script dependencies:** `scipy` (available in venv) is used for Wilson CI and Cochran-Armitage. `statsmodels` is NOT installed (not needed -- scripts use scipy directly). `scienceplots` is installed in venv (version 2.2.1). [VERIFIED: pip list]

**Figure generation note:** `pdflatex` is NOT installed on this machine. [VERIFIED: command -v] Figure generation may work for PNG/PDF output via matplotlib but will fail if scienceplots tries to use a LaTeX backend. Skip figure regeneration if it fails -- figures from Phase 19 are still valid for the non-XSBench content; XSBench figure changes are cosmetic.

### Expected Number Changes After Re-Run

After adding 32 XSBench files, the following are expected to change:
- GPT total tasks: 557 -> higher (new XSBench primary tasks added)
- GPT pass count and rate: will shift based on XSBench results
- GPT by_direction: directions that gained XSBench files (cuda-to-omp, cuda-to-opencl, omp-to-cuda, omp-to-opencl, opencl-to-cuda, opencl-to-omp) will have updated totals
- Cross-model comparison: chi2, p-value, Cohen's h will shift
- Per-kernel agreement: xsbench may rejoin as a common kernel (was removed because GPT only had 6 files)
- Error taxonomy: may shift for XSBench-related categories
- Self-repair stats: will change with new XSBench tasks
- Augmentation stats: L0-L4 counts will change
- pass@k: may change if new XSBench files include temperature=0.7 samples

**All 19-NUMBERS.md values are stale after XSBench addition.** The executor must generate fresh 20-NUMBERS.md.

## `% src:` Comment Convention [VERIFIED: grep of overleaf.tex]

Every numeric claim in the paper has a `% src:` comment on the same or preceding line. Format:

```latex
% src: paper_data_gpt41mini.json > primary_campaign > overall: 177/557=0.3178
% src: cross_model_comparison.json > overall > chi_squared: chi2=5.54, p=0.019
% src: error_taxonomy.json > build_fail_categories > missing_header > by_model (GPT=151)
```

Convention rules:
1. Every changed number MUST have its `% src:` comment updated to reflect the new value
2. Comments cite the JSON file path, the key path within the JSON, and the actual value
3. Combined/computed values show the arithmetic (e.g., `272+177=449 PASS`)
4. The comment goes on the SAME line as the LaTeX text, or on the line immediately above/below

**Count of existing GPT `% src:` comments in overleaf.tex:** ~50+ comments reference GPT/cross_model data [VERIFIED: grep count]

## 13 Structural Changes from 19-STRUCTURAL-CHANGES.md [VERIFIED: file read]

Each change has: file, section, approximate line range, old text, new text, rationale, source JSON.

| # | Change | Files | Key Complexity |
|---|--------|-------|----------------|
| 1 | Remove/rewrite "7 of 8 directions" footnote | paper.tex ~1047, overleaf.tex ~1104 | Footnote claim inverted -- omp_target-to-cuda now available, cuda-to-omp_target is the missing one |
| 2 | Update cross-model direction table | paper.tex ~1069, overleaf.tex ~1126 | 7 rows with new GPT rates, remove old cuda-to-omp_target row, add omp_target-to-cuda row |
| 3 | Rewrite effect-size discussion | paper.tex ~1146, overleaf.tex ~1203 | "4 of 7" -> "1 of 7", new largest effects, remove h=0.86 reference |
| 4 | Update per-direction table GPT column | paper.tex ~955, overleaf.tex ~987 | 6 existing rows updated + 2 case study rows get data |
| 5 | Flag XSBench coverage reduction | Various XSBench references | Qualification sentence about GPT XSBench coverage asymmetry |
| 6 | Update intro GPT numbers | paper.tex ~168, overleaf.tex ~172 | 29.2% -> 31.8%, chi2, p-value, h |
| 7 | Update overall pass rates table (Table 3) | paper.tex ~697, overleaf.tex ~740 | GPT row + Aggregate row + prose |
| 8 | Update failure taxonomy comparison | paper.tex ~1109, overleaf.tex ~1165 | BUILD_FAIL narrative less extreme, VERIFY_FAIL direction reversed |
| 9 | Update per-kernel agreement | paper.tex ~1131, overleaf.tex ~1187 | 31->29 kernels, 13->18 both-pass, kernel name lists |
| 10 | Update cross-model intro paragraph | paper.tex ~1050, overleaf.tex ~1107 | Overall stats, chi2, p-value, h |
| 11 | Update abstract GPT numbers | paper.tex ~82, overleaf.tex ~82 | Same stats as #6 |
| 12 | Update discussion GPT reference | paper.tex ~1176, overleaf.tex ~1233 | 29.2% -> 31.8% |
| 13 | Update conclusion GPT reference | paper.tex ~1252, overleaf.tex ~1309 | 29.2% -> 31.8%, p-value |

**Line numbers in 19-STRUCTURAL-CHANGES.md may be stale** after working tree changes shift lines. Always grep for anchor text.

## Appendices.tex Update Targets [VERIFIED: file read]

Three tables and one stats summary row need GPT column updates:

### 1. Self-Repair Table (tab:self-repair, ~line 1110-1128)
GPT column values to update from `paper_data_gpt41mini.json > primary_campaign > self_repair`:
- Total tasks: 551 -> new value
- First-attempt PASS: 119 (21.6%) -> new values
- Repaired: 42 (7.6%) -> new values
- Total PASS: 161 (29.2%) -> new values
- Relative improvement: +35.3% -> new values
- Persistent fail: 361 -> new value
- Regression: 5 (0.9%) -> new value
- Combined column: recalculate all rows (Qwen unchanged + new GPT)

### 2. Augmentation Table (tab:augmentation-rates, ~line 1132-1148)
GPT column values to update from `paper_data_gpt41mini.json > primary_campaign > augmentation > all_directions`:
- L0 through L4: rates, CIs, and n values
- GPT column header `n` value may change

### 3. Pass@k Table (tab:pass-at-k, ~line 1170-1183)
GPT row to update from `paper_data_gpt41mini.json > passk_campaign > aggregate_passk`:
- Greedy rate: 29.2% -> new value
- pass@1: 23.1% -> new value
- pass@3: 28.4% -> new value
- n_tasks: 88 -> may change
- Hard Fail, Noisy, Always Pass: counts may change

### 4. Statistical Summary Table (tab:stats-summary, ~line 1205-1222)
Two rows need updating:
- Model comparison (chi-squared) row: chi2=10.97, p=9.3e-4, Cramer's V=0.09 -> new values
- GPT augmentation (Cochran-Armitage) row: z=0.53, p=0.60 -> new values

## Additional Paper Locations with GPT Numbers [VERIFIED: grep]

Beyond the 13 structural changes, these locations also reference GPT numbers:

| Location | overleaf.tex line | Content | Source |
|----------|-------------------|---------|--------|
| Intro "1,261 primary tasks" | ~210 | Combined task count | 710 + new GPT total |
| Section 6 intro task counts | ~675 | "GPT-4.1~mini adds NNN tasks" | paper_data_gpt41mini.json > overall > total |
| Section 6.1 prose | ~700-705 | GPT pass rate, BUILD_FAIL %, chi2, h | paper_data_gpt41mini.json + cross_model |
| Section 6.3 per-kernel tiers | ~839 | "13 both-pass kernels...5 both-fail" | cross_model_comparison.json > per_kernel_matrix |
| Section 6.6 OpenCL asymmetry | ~920-955 | Direction table GPT column | paper_data_gpt41mini.json > by_direction |
| Section 6.8 augmentation | ~934+ | GPT Cochran-Armitage | paper_data_gpt41mini.json > augmentation |
| Per-kernel table in appendices | ~1227+ | Full 31-row table may reference GPT | Verify if GPT data appears |

## Wilson CI Computation [VERIFIED: source code]

The analysis scripts use a Wilson score CI implementation from scipy (not statsmodels). The formula is in `generate_paper_data.py` lines 98-115. For the Aggregate row recalculation:

```python
from scipy import stats as sp_stats
import math

def wilson_ci(passes, total, alpha=0.05):
    z = sp_stats.norm.ppf(1 - alpha / 2)
    p_hat = passes / total
    denom = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denom
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total) / denom
    return (round(max(0.0, center - spread), 4), round(min(1.0, center + spread), 4))

# After re-run: combined_pass = 272 + new_gpt_pass, combined_total = 710 + new_gpt_total
# ci = wilson_ci(combined_pass, combined_total)
```

## Common Pitfalls

### Pitfall 1: Using Stale 19-NUMBERS.md Values
**What goes wrong:** Numbers from 19-NUMBERS.md (generated with 910 GPT files) are used instead of freshly generated values (from 942 GPT files).
**Why it happens:** The 19-STRUCTURAL-CHANGES.md document includes specific old->new text with numeric values. After XSBench addition, all "new" values in that document are stale.
**How to avoid:** ALWAYS read from freshly generated JSON files after Task 0 re-run. Never use hardcoded values from 19-STRUCTURAL-CHANGES.md. Use that document only for WHAT to change (locations, structure), not for the actual numbers.
**Warning signs:** Numbers in the paper matching 19-NUMBERS.md exactly instead of fresh JSON values.

### Pitfall 2: Line Number Drift Between Files
**What goes wrong:** Editing paper.tex at the same line number as overleaf.tex, missing the target.
**Why it happens:** Different preamble lengths and section ordering create a variable offset.
**How to avoid:** Always grep for anchor text (e.g., the LaTeX label, a unique phrase) rather than using line numbers from 19-STRUCTURAL-CHANGES.md.
**Warning signs:** Edit applied to wrong section or missing entirely.

### Pitfall 3: Forgetting to Update `% src:` Comments
**What goes wrong:** Paper numbers updated but source comments still reference old values.
**Why it happens:** Comments are easy to overlook during find-and-replace.
**How to avoid:** For every numeric edit, update the `% src:` comment on the same line. Do a final grep to verify no stale `% src:` comments reference old values (e.g., `551`, `161/551`, `10.97`, `0.19`).
**Warning signs:** `grep -n "551\|10\.97\|0\.000926\|29\.2" overleaf.tex` returns hits in content lines.

### Pitfall 4: Breaking LaTeX Environment Balance
**What goes wrong:** Adding/removing table rows or environments without matching begin/end.
**Why it happens:** Cross-model direction table restructuring (removing a row, adding a row).
**How to avoid:** After editing, count `\begin{...}` and `\end{...}` occurrences and verify they match. The known invariant: overleaf.tex and paper.tex should have begin==end; appendices.tex has a known +1 pre-existing difference.
**Warning signs:** pdflatex errors about unmatched environments.

### Pitfall 5: Methodology Section Drift Between Files
**What goes wrong:** Attempting to synchronize methodology text between overleaf.tex and paper.tex when they are intentionally different.
**Why it happens:** D-11 says "apply the same methodology text edits to paper.tex" -- but the methodology edits are already applied in paper.tex working tree.
**How to avoid:** Verify with `git diff` that both files already have the same working tree methodology changes. They do. Phase 20 only needs to add GPT numeric changes to both files.

### Pitfall 6: Cramer's V vs Cohen's h Confusion
**What goes wrong:** Using Cohen's h value in the Cramer's V field of the stats summary table.
**Why it happens:** Both are effect size measures from the same cross-model comparison.
**How to avoid:** Cramer's V = sqrt(chi2 / total_n). Cohen's h is computed differently. Check the stats summary table carefully -- it uses Cramer's V, not Cohen's h.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wilson CI computation | Manual formula | `wilson_ci()` function in scripts or `from scipy.stats import norm` | Edge cases at p=0, p=1, small n |
| Aggregate row calculation | Mental arithmetic | Python script that sums Qwen+GPT counts and calls `wilson_ci()` | Arithmetic errors propagate to CI |
| Number extraction from JSON | Reading JSON visually | `python3 -c "import json; ..."` one-liners | Prevents transcription errors |
| Finding GPT number locations | Manual line counting | `grep -n` with specific anchor patterns | Line numbers drift between edits |
| Stale number detection | Manual comparison | `grep -c "29\.2\|551\|10\.97\|0\.19"` after edits | Catches forgotten locations |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | /validate (4-wave custom protocol, ~3 min) |
| Config file | Pre-commit hook enforces `.validation_passed` sentinel |
| Quick run command | `/validate` |
| Full suite command | `/validate` (same) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| D-01 | overleaf.tex GPT numbers match fresh JSONs | script | `python3 -c "...spot check..."` | Wave 0 |
| D-03 | appendices.tex GPT numbers match fresh JSONs | script | `grep -c "old_value" appendices.tex` | Wave 0 |
| D-05 | All 13 structural changes applied | manual + grep | grep for old text patterns | Wave 0 |
| D-13 | /validate passes | protocol | `/validate` | Existing |
| D-14 | pdflatex check | manual | `pdflatex -interaction=nonstopmode overleaf.tex` | N/A (pdflatex not installed) |

### Sampling Rate
- **Per task commit:** Spot-check script (10+ numbers against source JSONs)
- **Per wave merge:** `/validate`
- **Phase gate:** Full `/validate` green before commit

### Wave 0 Gaps
- [ ] Spot-check script: verify 10+ specific GPT numbers in each file against source JSONs
- [ ] Stale number detector: grep for known old values (29.2, 551, 10.97, 0.000926, 0.19, 316, 161) in content lines

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Analysis scripts | Yes | 3.12.3 | -- |
| scipy | Wilson CI, stats | Yes | 1.17.1 | -- |
| scienceplots | Figure generation | Yes | 2.2.1 | Skip figures if fails |
| matplotlib | Figure generation | Yes | 3.6.3 | -- |
| pdflatex | D-14 LaTeX check | **No** | -- | Skip silently (per D-14) |
| statsmodels | Wilson CI (CONTEXT suggestion) | **No** | -- | Use scipy wilson_ci() from scripts |

**Missing dependencies with no fallback:** None (pdflatex skip is explicitly allowed by D-14).

**Missing dependencies with fallback:**
- `pdflatex` not installed -- skip the compilation check silently as D-14 permits.
- `statsmodels` not installed -- use the `wilson_ci()` function from `generate_paper_data.py` which uses scipy only.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | 32 new XSBench files are valid (not empty-prompt Argonne artifacts) | Analysis Pipeline Re-Run | Numbers would still be wrong; Task 0 output would reveal this via anomalous counts |
| A2 | Figure regeneration can be skipped if it fails (Phase 19 figures are still acceptable) | Environment Availability | Figures may show slightly different XSBench bars; cosmetic only |
| A3 | The methodology sections in overleaf.tex and paper.tex are intentionally different and should not be synchronized | Methodology Section Differences | If they should be synced, Phase 20 scope would expand significantly |

## Open Questions

1. **Will XSBench rejoin the common-kernel set after re-run?**
   - What we know: XSBench was removed from common kernels (29 not 31) because GPT only had 6 files covering 2 directions. Now GPT has 38 files covering 6 directions.
   - What's unclear: Whether the analysis scripts count XSBench as a "common kernel" depends on the overlap logic (both models must have at least one primary result for the kernel).
   - Recommendation: Run Task 0, then read fresh `cross_model_comparison.json > per_kernel_matrix` to determine if total_common_kernels changed from 29.

2. **Exact GPT total after XSBench addition?**
   - What we know: Was 557 primary tasks with 910 files. Now 942 files on disk.
   - What's unclear: How many of the 32 new files are primary (temp=0.0) vs pass@k (temp=0.7).
   - Recommendation: Task 0 output will show the exact breakdown. Parse from fresh `paper_data_gpt41mini.json > file_counts`.

## Sources

### Primary (HIGH confidence)
- `19-STRUCTURAL-CHANGES.md` -- all 13 structural change specifications [read in full]
- `19-NUMBERS.md` -- Phase 19 reference numbers [read in full, but stale after XSBench]
- `19-01-SUMMARY.md` -- Phase 19 execution summary [read]
- `overleaf.tex`, `paper.tex`, `appendices.tex` -- current file state [verified via git diff, grep, wc]
- Analysis script `--help` outputs -- CLI invocations [verified]
- `generate_paper_data.py` source -- Wilson CI implementation [verified lines 95-115]

### Secondary (MEDIUM confidence)
- `20-01-PLAN.md` -- reference plan (premature done markers, but task structure is useful) [read]
- `20-CONTEXT.md` -- user decisions and canonical references [read in full]

## Metadata

**Confidence breakdown:**
- File state and diffs: HIGH -- directly verified via git diff, grep, wc
- Analysis pipeline CLIs: HIGH -- verified via --help
- 19-STRUCTURAL-CHANGES.md locations: MEDIUM -- line numbers may have shifted, but anchor text is reliable
- Post-XSBench number predictions: LOW -- actual values depend on Task 0 re-run output

**Research date:** 2026-04-08
**Valid until:** 2026-04-09 (one-day validity -- numbers change after Task 0)
