# Phase 7: Full Analysis Regeneration - Research

**Researched:** 2026-04-04
**Domain:** Analysis script execution and data regeneration
**Confidence:** HIGH

## Summary

Phase 7 is an execution-focused phase: run 8 analysis scripts in sequence against the now-complete 1,248-file Qwen 3.5 397B evaluation dataset, then verify that the outputs are correct and complete. No new code needs to be written. The scripts already exist, have well-defined CLI interfaces, and auto-discover result files by walking `results/evaluation/{model}/` directories. The critical insight is that ALL scripts read raw result JSONs independently -- there are ZERO data dependencies between analysis outputs -- so scripts can technically run in any order or even in parallel.

The primary risk is verification: several REGEN requirements (03, 04, 05) demand cross-suite breakdowns, but the current scripts (`build_error_taxonomy.py`, `selfrepair_analysis.py`, `statistical_analysis.py`) do not produce explicit per-suite groupings. They DO process all suites' data, so non-Rodinia kernels appear in the output grouped by kernel name. Verification must check for the PRESENCE of non-Rodinia kernel names (e.g., `floydwarshall`, `xsbench`, `rsbench`, `mixbench`) in the output rather than looking for a `by_suite` top-level key.

**Primary recommendation:** Execute scripts in the order specified in the ROADMAP, verify each output's record count and cross-suite kernel coverage, and handle `paper_data.json` carefully (two separate runs: Rodinia-only and full-dataset).

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REGEN-01 | `eval_summary.json` reflects all 1,248 Qwen result files across 5 suites | `analyze_eval.py --model together-qwen-3.5-397b-a17b` with `--project-root .` will load all 1,248 files, exclude 112 KNOWN_FAIL-involved results, producing `total_tasks: 1136`. The "1,248" count is files on disk; `total_tasks` is post-exclusion. Verify BOTH: file count matches 1,248 on disk, `total_tasks` matches 1,136 post-exclusion. |
| REGEN-02 | `paper_data.json` regenerated twice: Rodinia-only (480-task scope) and full (1,248-task) | Run `--suite rodinia --output paper_data_rodinia.json` first, then run without `--suite --output paper_data.json`. Current `paper_data.json` IS Rodinia-only (suite_filter: rodinia, 480 primary). After Phase 7, `paper_data.json` becomes full-dataset and `paper_data_rodinia.json` preserves Section 6.1-6.5 scope. |
| REGEN-03 | `error_taxonomy.json` covers failure modes across ALL suites | Script walks all model dirs and loads all results. Verify by checking `per_kernel` keys for non-Rodinia kernels (e.g., `floydwarshall`, `xsbench`, `rsbench`, `mixbench-*`). No explicit `by_suite` key exists. |
| REGEN-04 | `selfrepair_analysis.json` includes cross-suite self-repair rates | Script loads all results. Verify `by_kernel` section contains non-Rodinia kernel names. No explicit per-suite breakdown. |
| REGEN-05 | `statistical_analysis.json` includes cross-suite statistical tests | Script imports `load_results` from `analyze_eval.py`, loads all results. Wilson CIs are computed by model, direction, kernel, and level -- not by suite. Verify `wilson_cis.by_kernel` contains non-Rodinia kernels. |
| REGEN-06 | `sloc_analysis.json` unchanged from Phase 2 | Already covers all 35 kernels (verified). Do NOT re-run `sloc_analysis.py`. Just validate the existing file is intact. |
| REGEN-07 | `token_analysis.json` includes cost estimates for all 1,248 tasks | Script loads all results after KNOWN_FAIL exclusion. Current file is stale (March 31, 906 results). After regeneration, verify `total_results` matches 1,136 (post-exclusion count, since token_analysis also excludes KNOWN_FAIL). |
| REGEN-08 | `benchmark_characterization.json` unchanged | Run `validate_characterization.py` only (validation, not regeneration). Must produce zero errors. |
| REGEN-09 | `translation_complexity.csv` covers all suites | ALREADY COVERS all 5 suites (290 rows: 110 rodinia, 150 hecbench, 12 xsbench, 12 rsbench, 6 mixbench). The ROADMAP concern about "Rodinia+XSBench only" is stale. Regenerate anyway to confirm; verify row count and suite distribution. |
| REGEN-10 | If Phase 3 plan 03-01 completed: `augmentation_per_kernel_matrix.json` also regenerated | Phase 3 plan 03-01 is NOT yet completed (STATE.md: "Phase 3 context gathered"). However, `augmentation_per_kernel_matrix.json` EXISTS (created April 4 by worktree work). If no standalone regeneration script exists, skip regeneration and validate existing file. |
</phase_requirements>

## Standard Stack

No new libraries needed. All scripts use the existing project dependencies.

### Core Scripts (Phase 7 Execution Targets)

| Script | Location | CLI | Outputs |
|--------|----------|-----|---------|
| analyze_eval.py | `scripts/evaluation/` | `--project-root . --model together-qwen-3.5-397b-a17b` | `eval_summary.json` + `eval_summary.md` |
| generate_paper_data.py | `scripts/analysis/` | `--suite rodinia --output ... -v` OR `--output ... -v` | `paper_data_rodinia.json` OR `paper_data.json` (JSON only, no MD) |
| build_error_taxonomy.py | `scripts/analysis/` | `--project-root .` | `error_taxonomy.json` + `error_taxonomy.md` |
| selfrepair_analysis.py | `scripts/analysis/` | `--project-root .` | `selfrepair_analysis.json` + `selfrepair_analysis.md` |
| statistical_analysis.py | `scripts/analysis/` | `--project-root . -v` | `statistical_analysis.json` + `statistical_analysis.md` |
| token_analysis.py | `scripts/analysis/` | `--project-root .` | `token_analysis.json` + `token_analysis.md` |
| classify_translation_pairs.py | `scripts/analysis/` | `--project-root .` | `translation_complexity.csv` |
| validate_characterization.py | `scripts/analysis/` | `--project-root .` | `characterization_validation.txt` (console output) |

### Supporting Dependencies

| Library | Version | Purpose | Verified |
|---------|---------|---------|----------|
| scipy | 1.17.1 | Wilson CIs, chi-squared, Cochran-Armitage (statistical_analysis.py, generate_paper_data.py) | [VERIFIED: python3 -c import check] |
| numpy | 2.4.3 | Numerical computation in statistical tests | [VERIFIED: python3 -c import check] |

## Architecture Patterns

### Data Flow (Critical Insight: No Inter-Script Dependencies)

```
results/evaluation/together-qwen-3.5-397b-a17b/*.json  (1,248 files)
    |
    +---> analyze_eval.py ---------> eval_summary.json + .md
    +---> generate_paper_data.py --> paper_data.json (or paper_data_rodinia.json)
    +---> build_error_taxonomy.py -> error_taxonomy.json + .md
    +---> selfrepair_analysis.py --> selfrepair_analysis.json + .md
    +---> statistical_analysis.py -> statistical_analysis.json + .md
    +---> token_analysis.py -------> token_analysis.json + .md
    |
specs/ + manifest.jsonl
    +---> classify_translation_pairs.py -> translation_complexity.csv
    |
results/analysis/benchmark_characterization.json (Phase 2 output)
    +---> validate_characterization.py -> console output (validation only)
```

**Key insight:** Every analysis script reads raw result JSONs independently. No script reads another script's output. This means execution order does not matter for correctness -- only for logical grouping in the plan.

### KNOWN_FAIL Exclusion Behavior

| Script | Exclusion Method | Excluded Specs |
|--------|-----------------|----------------|
| analyze_eval.py | `EXCLUDED_SPECS` frozenset (6 Rodinia specs) | Filters during load | [VERIFIED: source code] |
| generate_paper_data.py | `EXCLUDED_SPECS` frozenset (same 6) | Filters after load | [VERIFIED: source code] |
| build_error_taxonomy.py | NO exclusion | Processes ALL results including KNOWN_FAIL | [VERIFIED: source code] |
| selfrepair_analysis.py | NO exclusion | Processes ALL results | [VERIFIED: source code] |
| statistical_analysis.py | Imports `load_results` from `analyze_eval.py` | Same 6 specs excluded | [VERIFIED: source code] |
| token_analysis.py | `EXCLUDED_SPECS` frozenset (same 6) | Filters during load | [VERIFIED: source code] |

**Important nuance:** `build_error_taxonomy.py` and `selfrepair_analysis.py` do NOT exclude KNOWN_FAIL specs. This means their total counts will differ from other scripts. For error_taxonomy, this is actually correct behavior -- KNOWN_FAIL spec translations still have real failure modes worth analyzing. For selfrepair, the difference is minor (most KNOWN_FAIL-involving tasks are single-attempt failures).

### Suite Detection in Outputs

None of the scripts produce a top-level `by_suite` grouping. To verify cross-suite coverage:

| Requirement | What to Check |
|-------------|---------------|
| REGEN-03 (error_taxonomy) | `per_kernel` dict should contain keys like `floydwarshall`, `xsbench`, `rsbench`, `mixbench`, `convolution1d`, etc. |
| REGEN-04 (selfrepair) | `by_kernel` dict should contain non-Rodinia kernel names |
| REGEN-05 (statistical) | `wilson_cis.by_kernel` should contain non-Rodinia kernel names |

[VERIFIED: source code inspection -- scripts walk ALL results, but group by kernel/direction/model/level, never by suite]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Suite-specific paper_data | Don't modify generate_paper_data.py | Use `--suite rodinia` flag and `--output` for Rodinia-only | Flag already exists and is tested |
| Cross-suite verification | Don't add per-suite grouping to scripts | Verify kernel names in output contain non-Rodinia entries | Adding suite grouping is a code change that risks breaking existing behavior |
| Analysis file freshness | Don't compare timestamps manually | Re-run ALL scripts; compare before/after record counts | Stale files are the problem this phase solves |

## Common Pitfalls

### Pitfall 1: Overwriting paper_data.json Before Creating Rodinia-Only Version
**What goes wrong:** Running `generate_paper_data.py` without `--suite` first would overwrite the existing Rodinia-only `paper_data.json` with full-dataset data, losing the 480-task Section 6 baseline.
**Why it happens:** Current `paper_data.json` IS the Rodinia-only file (suite_filter: rodinia).
**How to avoid:** Run in this EXACT order: (1) `--suite rodinia --output paper_data_rodinia.json` FIRST, (2) `--output paper_data.json` SECOND. This creates the new Rodinia-only file before overwriting the old one.
**Warning signs:** `paper_data.json` has `suite_filter: null` and primary_campaign total > 480.

### Pitfall 2: Misinterpreting "1,248 Files" as total_tasks
**What goes wrong:** REGEN-01 says "reflects all 1,248 Qwen result files." But `eval_summary.json`'s `total_tasks` will be ~1,136 (post-KNOWN_FAIL exclusion), not 1,248.
**Why it happens:** 112 result files involve KNOWN_FAIL specs and are excluded by `analyze_eval.py`.
**How to avoid:** Verify BOTH: (a) 1,248 JSON files exist on disk (`find ... | wc -l`), AND (b) `total_tasks` is ~1,136 (1,248 - 112 excluded).
**Warning signs:** `total_tasks` being 907 (old value) instead of ~1,136.

### Pitfall 3: Forgetting to Activate venv
**What goes wrong:** Scripts fail with ImportError for scipy, numpy, etc.
**Why it happens:** Python packages are installed in `env_parbench`, not system-wide.
**How to avoid:** Always `source env_parbench/bin/activate` before running scripts.
**Warning signs:** `ModuleNotFoundError: No module named 'scipy'`.

### Pitfall 4: Running sloc_analysis.py or benchmark_characterization.py
**What goes wrong:** Re-running these would overwrite Phase 2's canonical outputs.
**Why it happens:** These files are Phase 2 outputs that should NOT change.
**How to avoid:** REGEN-06 says "re-validate, don't recompute." REGEN-08 says "validate_characterization.py passes with zero errors." Neither requires regeneration.
**Warning signs:** `sloc_analysis.json` or `benchmark_characterization.json` timestamps change.

### Pitfall 5: Translation Complexity CSV Concern is Stale
**What goes wrong:** Wasting time debugging `classify_translation_pairs.py` for missing suites.
**Why it happens:** ROADMAP says "currently Rodinia+XSBench only -- may need script update." This is STALE information.
**How to avoid:** `translation_complexity.csv` ALREADY covers all 5 suites (290 rows). Regenerating will confirm, not fix. [VERIFIED: `cut -d',' -f1 translation_complexity.csv | sort | uniq -c`]

### Pitfall 6: generate_paper_data.py Has No Markdown Companion
**What goes wrong:** REGEN-12 requires "all Markdown companion files regenerated alongside JSON counterparts." But `generate_paper_data.py` only produces JSON.
**Why it happens:** The script was designed for machine-readable paper data, not human-readable reports.
**How to avoid:** This is NOT a failure -- paper_data.json legitimately has no .md companion. Verify all OTHER scripts produce both JSON + MD.

## Code Examples

### Exact Execution Commands (verified from source code)

```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

# 1. Aggregate eval summary (reads ALL model dirs, filters to Qwen)
python3 scripts/evaluation/analyze_eval.py \
    --project-root . --model together-qwen-3.5-397b-a17b

# 2a. Paper data -- Rodinia primary campaign (480 tasks)
python3 scripts/analysis/generate_paper_data.py \
    --suite rodinia --output results/analysis/paper_data_rodinia.json -v

# 2b. Paper data -- ALL suites (full 1,248-task dataset)
python3 scripts/analysis/generate_paper_data.py \
    --output results/analysis/paper_data.json -v

# 3. Error taxonomy
python3 scripts/analysis/build_error_taxonomy.py --project-root .

# 4. Self-repair analysis
python3 scripts/analysis/selfrepair_analysis.py --project-root .

# 5. Statistical analysis
python3 scripts/analysis/statistical_analysis.py --project-root . -v

# 6. Token analysis
python3 scripts/analysis/token_analysis.py --project-root .

# 7. Translation complexity
python3 scripts/analysis/classify_translation_pairs.py --project-root .

# 8. Validate characterization (validation only, no regeneration)
python3 scripts/analysis/validate_characterization.py --project-root .
```

[VERIFIED: CLI arguments confirmed from argparse definitions in each script's source code]

### Verification Commands

```bash
# REGEN-01: Verify eval_summary total_tasks
python3 -c "
import json
with open('results/evaluation/eval_summary.json') as f:
    d = json.load(f)
qwen = d['by_model']['together-qwen-3.5-397b-a17b']
print(f'total_tasks: {qwen[\"total\"]}, pass: {qwen[\"pass\"]}, rate: {qwen[\"rate\"]}')
assert qwen['total'] > 1000, f'Expected >1000, got {qwen[\"total\"]}'
"

# REGEN-02: Verify both paper_data files exist and differ
python3 -c "
import json
with open('results/analysis/paper_data_rodinia.json') as f:
    rod = json.load(f)
with open('results/analysis/paper_data.json') as f:
    full = json.load(f)
print(f'Rodinia: suite_filter={rod[\"suite_filter\"]}, primary={rod[\"file_counts\"][\"primary_campaign\"]}')
print(f'Full: suite_filter={full[\"suite_filter\"]}, primary={full[\"file_counts\"][\"primary_campaign\"]}')
assert rod['suite_filter'] == 'rodinia'
assert full['suite_filter'] is None
assert full['file_counts']['primary_campaign'] > rod['file_counts']['primary_campaign']
"

# REGEN-03/04/05: Verify non-Rodinia kernels in outputs
python3 -c "
import json
non_rodinia = {'floydwarshall','xsbench','rsbench','mixbench','scan','babelstream','convolution1d','stencil1d','aes','reduction'}
for name, path in [
    ('error_taxonomy', 'results/analysis/error_taxonomy.json'),
    ('selfrepair', 'results/analysis/selfrepair_analysis.json'),
    ('statistical', 'results/analysis/statistical_analysis.json'),
]:
    with open(path) as f:
        d = json.load(f)
    if name == 'error_taxonomy':
        kernels = set(d.get('per_kernel', {}).keys())
    elif name == 'selfrepair':
        kernels = set(d.get('by_kernel', {}).keys())
    elif name == 'statistical':
        kernels = set(d.get('wilson_cis', {}).get('by_kernel', {}).keys())
    found = kernels & non_rodinia
    print(f'{name}: found {len(found)} non-Rodinia kernels: {sorted(found)[:5]}...')
    assert len(found) >= 3, f'Expected >=3 non-Rodinia kernels in {name}, found {len(found)}'
"

# REGEN-07: Verify token analysis total
python3 -c "
import json
with open('results/analysis/token_analysis.json') as f:
    d = json.load(f)
print(f'total_results: {d[\"total_results\"]}')
assert d['total_results'] > 1000
"

# REGEN-09: Verify translation_complexity.csv suite coverage
python3 -c "
import csv
from collections import Counter
with open('results/evaluation/translation_complexity.csv') as f:
    reader = csv.DictReader(f)
    suites = Counter(r['suite'] for r in reader)
print('Suite distribution:', dict(suites))
assert len(suites) == 5, f'Expected 5 suites, got {len(suites)}'
"
```

[VERIFIED: These verification patterns are based on actual field names in the current JSON files]

## Current File State (Pre-Phase 7 Baseline)

| File | Date | Records/Tasks | Stale? | Action |
|------|------|---------------|--------|--------|
| eval_summary.json | Apr 1 | 907 (Qwen total) | YES | Regenerate |
| paper_data.json | Apr 3 | 480 primary (Rodinia-only) | YES (scope) | Regenerate as paper_data_rodinia.json; create new full-dataset paper_data.json |
| error_taxonomy.json | Mar 31 | 1,018 total | LIKELY STALE | Regenerate |
| selfrepair_analysis.json | Apr 3 | 1,248 total | Possibly current | Regenerate to confirm |
| statistical_analysis.json | Apr 3 | 1,136 total | Possibly current | Regenerate to confirm |
| token_analysis.json | Mar 31 | 906 total | YES | Regenerate |
| sloc_analysis.json | Apr 3 | 35 kernels | Current | DO NOT regenerate; validate only |
| benchmark_characterization.json | Apr 3 | 7 sections | Current | DO NOT regenerate; validate only |
| translation_complexity.csv | Mar 30 | 290 pairs | Possibly current | Regenerate to confirm |
| augmentation_per_kernel_matrix.json | Apr 4 | -- | Recent | Conditional on Phase 3 |

[VERIFIED: Timestamps from `stat` command; record counts from `python3 -c` JSON inspection]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The 112 KNOWN_FAIL exclusion count is correct (1,248 - 112 = 1,136) | Phase Requirements, Pitfall 2 | Verification assertions would fail with wrong expected count; easy to detect |
| A2 | `selfrepair_analysis.py` will include non-Rodinia kernels in `by_kernel` output | Phase Requirements REGEN-04 | If script internally filters to Rodinia, verification would catch it |
| A3 | Running `generate_paper_data.py` without `--suite` will produce full-dataset output (not default to some hardcoded suite) | Phase Requirements REGEN-02 | The `--suite` default is `None` per argparse; verified in source. LOW risk. |

All A1-A3 are LOW risk -- source code inspection confirms the behavior, and verification scripts will catch any discrepancies.

## Open Questions (RESOLVED)

1. **REGEN-01 interpretation: 1,248 or 1,136?**
   - What we know: 1,248 files on disk; 1,136 after KNOWN_FAIL exclusion; `eval_summary.json` reports post-exclusion count.
   - What's unclear: The requirement says "reflects all 1,248 Qwen result files." Does this mean the JSON should report 1,248 or 1,136?
   - RESOLVED: Verify BOTH (files on disk = 1,248; `total_tasks` in summary = 1,136). Document the 112-file exclusion in the verification output.

2. **REGEN-10: Augmentation matrix regeneration**
   - What we know: Phase 3 plan 03-01 is NOT completed. But `augmentation_per_kernel_matrix.json` EXISTS (created Apr 4).
   - What's unclear: Whether a standalone regeneration script exists (none found in `scripts/`).
   - RESOLVED: Skip regeneration; validate existing file. If Phase 3 produces a script later, Phase 7 can re-run it.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | pyproject.toml |
| Quick run command | `python3 -m pytest scripts/analysis/test_generate_paper_data.py -x` |
| Full suite command | `python3 -m pytest scripts/analysis/ -x -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REGEN-01 | eval_summary covers 1,136+ tasks | smoke | `python3 -c "import json; d=json.load(open('results/evaluation/eval_summary.json')); assert d['by_model']['together-qwen-3.5-397b-a17b']['total'] > 1000"` | N/A (inline) |
| REGEN-02 | Two paper_data files, different scopes | smoke | `python3 -c "[see verification commands above]"` | N/A (inline) |
| REGEN-03 | error_taxonomy has non-Rodinia kernels | smoke | `python3 -c "[see verification commands above]"` | N/A (inline) |
| REGEN-04 | selfrepair has non-Rodinia kernels | smoke | `python3 -c "[see verification commands above]"` | N/A (inline) |
| REGEN-05 | statistical has non-Rodinia kernels | smoke | `python3 -c "[see verification commands above]"` | N/A (inline) |
| REGEN-06 | sloc_analysis unchanged | smoke | Check file unchanged (compare checksum before/after) | N/A |
| REGEN-07 | token_analysis covers 1,000+ tasks | smoke | `python3 -c "import json; assert json.load(open('results/analysis/token_analysis.json'))['total_results'] > 1000"` | N/A (inline) |
| REGEN-08 | characterization validation passes | smoke | `python3 scripts/analysis/validate_characterization.py --project-root .` | Exists |
| REGEN-09 | translation_complexity has 5 suites | smoke | `python3 -c "[see verification commands above]"` | N/A (inline) |
| REGEN-10 | augmentation matrix (conditional) | manual-only | Check Phase 3 status; validate existing file if present | N/A |

### Sampling Rate
- **Per task commit:** Run verification commands after each script execution
- **Per wave merge:** Full verification suite (all REGEN checks)
- **Phase gate:** All 10 REGEN checks green before marking complete

### Wave 0 Gaps
None -- no new test infrastructure needed. All verification is inline python commands against output JSON files.

## Sources

### Primary (HIGH confidence)
- [Source code] `scripts/evaluation/analyze_eval.py` -- CLI arguments (lines 442-513), load_results (lines 80-117), EXCLUDED_SPECS (lines 47-54)
- [Source code] `scripts/analysis/generate_paper_data.py` -- CLI arguments (lines 1138-1166), suite filter logic (lines 1188-1199), EXCLUDED_SPECS (lines 42-49)
- [Source code] `scripts/analysis/build_error_taxonomy.py` -- CLI arguments (lines 999-1006), load_results (lines 453-474), NO suite grouping
- [Source code] `scripts/analysis/selfrepair_analysis.py` -- CLI arguments (lines 108-116), load_all_results (lines 89-105), NO suite grouping
- [Source code] `scripts/analysis/statistical_analysis.py` -- CLI arguments (lines 1080-1117), imports load_results from analyze_eval (line 46), compute_all_cis (lines 810-837)
- [Source code] `scripts/analysis/token_analysis.py` -- CLI arguments (lines 177-185), load_all_results (lines 79-98), MODEL_PRICING (lines 34-42)
- [Source code] `scripts/analysis/classify_translation_pairs.py` -- reads manifest.jsonl + specs (lines 73-137), already covers all 5 suites
- [Source code] `scripts/analysis/validate_characterization.py` -- reads benchmark_characterization.json (line 659), validation only
- [File system] `results/evaluation/together-qwen-3.5-397b-a17b/` -- 1,248 JSON files confirmed via `find | wc -l`
- [File system] `results/evaluation/translation_complexity.csv` -- 290 data rows covering 5 suites confirmed via `cut | sort | uniq -c`
- [File system] `results/analysis/*.json` -- timestamps and record counts verified via `stat` and `python3 -c` inspection

### Secondary (MEDIUM confidence)
- None -- all findings verified against source code and file system

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries; all scripts verified in source
- Architecture: HIGH -- data flow verified by reading load functions and CLI args
- Pitfalls: HIGH -- identified from actual data inspection (stale counts, missing MD companions)
- Verification: HIGH -- verification commands tested against current file contents

**Research date:** 2026-04-04
**Valid until:** 2026-04-08 (paper submission deadline; phase must complete before then)
