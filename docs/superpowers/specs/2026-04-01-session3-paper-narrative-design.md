# Session 3 Design: Paper Narrative — Results & Discussion (Qwen-First)

**Date:** 2026-04-01
**Owner:** Samyak
**Objective:** Fill all [PENDING] placeholders in S6 (Results) and S7 (Discussion) using
verified data from on-disk result files, incorporating key findings and fixing known issues.

---

## Context

### Why This Work Is Needed
The paper_draft.md has ~81 [PENDING] markers in S6/S7/Abstract. The Session 2b analysis
scripts generated `statistical_analysis.json`, `error_taxonomy.json`, and
`selfrepair_analysis.json` — but these JSONs have **critical data integrity issues**
discovered during this design session:

1. **Campaign mixing bug**: `augmentation_curves` and `Fisher exact test` in
   `statistical_analysis.py` mix primary campaign (temp=0.0, L0-L4) with pass@k campaign
   (temp=0.7, L0 only), producing misleading augmentation numbers (22.6% vs correct 38.5%)
2. **1018 vs 906 vs 480**: Three different denominators exist across analysis outputs.
   Error taxonomy uses 1018 (all files including KNOWN_FAIL). Eval summary uses 906
   (excluding KNOWN_FAIL but mixing campaigns). Correct primary campaign count is 480.
3. **7 mislabeled results**: `rodinia-backprop-cuda-to-rodinia-backprop-opencl` at
   L0/s0/s1/s2/L2/L3/L4 — verify passed but `overall_status` = VERIFY_FAIL.

### Two Evaluation Campaigns On Disk

| Campaign | Temperature | Purpose | Levels | Files | Overall Pass Rate |
|----------|------------|---------|--------|-------|-------------------|
| **Primary** | 0.0 (deterministic) | Main results, pass@1 | L0-L4 | 480 | 170/480 = 35.4% |
| **Pass@k** | 0.7 (stochastic) | Sample diversity, pass@3 | L0 only | 426 | 81/426 = 19.0% |

Total on disk: 1018 files (includes 112 KNOWN_FAIL). After exclusion: 906 = 480 + 426.

### Approach: Fresh Analysis Script + Agent Team Paper Writing

Instead of patching the buggy existing analysis scripts, write one clean
`generate_paper_data.py` that produces exactly the tables the paper needs,
then use an agent team to fill the paper sections.

---

## Phase A: Data Pipeline (generate_paper_data.py)

### A.1 Fix 7 Mislabeled Results

Fix on disk: set `overall_status` to `"PASS"` in these 7 files:
- `rodinia-backprop-cuda-to-rodinia-backprop-opencl.json`
- `rodinia-backprop-cuda-to-rodinia-backprop-opencl-s0.json`
- `rodinia-backprop-cuda-to-rodinia-backprop-opencl-s1.json`
- `rodinia-backprop-cuda-to-rodinia-backprop-opencl-s2.json`
- `rodinia-backprop-cuda-to-rodinia-backprop-opencl-L2.json`
- `rodinia-backprop-cuda-to-rodinia-backprop-opencl-L3.json`
- `rodinia-backprop-cuda-to-rodinia-backprop-opencl-L4.json`

All are in `results/evaluation/together-qwen-3.5-397b-a17b/`.

**Post-fix primary campaign pass rate:** ~177/480 = 36.9% (7 flips from VERIFY_FAIL to PASS,
but only 3 of the 7 are in the primary campaign: L2, L3, L4; the bare .json and s0/s1/s2
have augment_level=0 — bare is primary, s0-s2 are pass@k).

### A.2 Write generate_paper_data.py

**Location:** `scripts/analysis/generate_paper_data.py`

**Input:** Reads all files from `results/evaluation/{model}/*.json`

**Processing:**
1. Load all result files
2. Exclude KNOWN_FAIL specs (same `EXCLUDED_SPECS` set)
3. Split by temperature: primary (temp=0.0) vs pass@k (temp=0.7)
4. For each campaign, compute:

**Output:** `results/analysis/paper_data.json` with these sections:

```
{
  "generated_at": "...",
  "primary_campaign": {
    "total": 480,
    "overall": {status_breakdown},
    "by_direction": {direction: {status_breakdown}},
    "by_kernel": {kernel: {status_breakdown}},
    "by_level": {level: {status_breakdown}},
    "augmentation": {
      "all_directions": {L0-L4 pass rates with n=96 each},
      "cuda_to_omp_balanced": {L0-L4 with n=16 per level},
      "cochran_armitage": {z, p, significant},
      "per_direction_by_level": {direction: {level: counts}}
    },
    "direction_asymmetry": {pair: {McNemar stats}},
    "self_repair": {breakdown from attempts[] field},
    "build_fail_subcategories": {category: count},
    "run_fail_subcategories": {category: count},
    "verify_fail_subcategories": {category: count}
  },
  "passk_campaign": {
    "total": 426,
    "overall": {status_breakdown},
    "by_direction": {direction: {status_breakdown}},
    "passk_estimates": {(kernel, direction): {n, c, pass@1}}
  },
  "sample_size_flags": [...],
  "wilson_cis": {per primary campaign slices}
}
```

**Error taxonomy classification** — reuse the regex patterns from `build_error_taxonomy.py`
for BUILD_FAIL subcategories (missing_header, undeclared_identifier, linker_error, etc.),
RUN_FAIL subcategories (segfault, opencl_jit_error, wrong_exit_code, etc.), and
VERIFY_FAIL subcategories (wrong_numerical_output, pass_overall_mislabel, etc.).

**Statistical tests** — reuse functions from `statistical_analysis.py`:
- Wilson score CIs for all rates
- Cochran-Armitage trend test (primary campaign, cuda-to-omp balanced subset, n=16 per level)
- McNemar exact test (primary campaign, L0 only, per direction pair)
- No model comparison chi-squared (single model)

### A.3 Verify Output

Run the script, inspect paper_data.json, verify:
- Primary total = 480 (post mislabel fix)
- Pass@k total = 426
- Augmentation L0 rate for all-directions matches ~38.5% (not 22.6%)
- Cochran-Armitage p ≈ 0.87

---

## Phase B: Paper Writing (Agent Team)

### B.1 Fill S6 Sections (~40 [PENDING] markers)

Using paper_data.json as the sole data source:

**S6.1 Overall Pass Rates:**
- Table 7: Qwen 3.5 row with 5-status breakdown from primary campaign
- Gemini row: [PENDING: Gemini — Session 5]
- Prose: describe 35.4% (or post-fix rate) with emphasis on failure mode distribution

**S6.2 Failure Taxonomy (the rich story):**
- Figure 5: Pie/bar of BUILD_FAIL (31%) / RUN_FAIL (23%) / VERIFY_FAIL (11%)
- BUILD_FAIL subcategories table: missing_header, undeclared_identifier, linker_error...
- RUN_FAIL subcategories: opencl_jit_error dominates when target is OpenCL
- VERIFY_FAIL subcategories: wrong_numerical_output dominates
- Direction × failure mode table showing WHY each direction fails differently
- Integrate Finding 1 (lavamd multi-file consistency failure) inline

**S6.3 Per-Kernel Analysis:**
- Table 8: 18-kernel × {PASS, BUILD, RUN, VERIFY, EXTR} matrix
- Difficulty tiers: Easy (>60%), Medium (40-60%), Hard (<40%), Impossible (0%)
- Per-tier characteristics: heartwall/myocyte always fail on missing headers,
  gaussian fails on wrong output, etc.

**S6.4 Self-Repair:**
- Table 9: first-attempt PASS vs repaired vs persistent vs regression
- Per-initial-failure repair rates: EXTRACTION_FAIL most recoverable (55.6%)
- Regression analysis: 6 cases where retry made things worse

**S6.5 Augmentation Robustness (REWRITTEN — null result):**
- Table 10: L0-L4 pass rates from primary campaign (all directions, n=96 each)
- Cochran-Armitage: z=-0.17, p=0.87 — no trend
- Per-direction breakdown showing flat curves across all directions
- Framing: model is robust to surface transforms → against memorization hypothesis

**S6.6 Cross-Direction Analysis:**
- Table 11: 6-direction pass rates from primary campaign
- McNemar tests: no significant asymmetry in any pair
- Discussion of absolute gap (cuda-to-omp 65% vs opencl-to-cuda 7%)
  with failure mode explanation (BUILD_FAIL vs RUN_FAIL patterns)

**S6.7 Pass@k Analysis:**
- Table 12: pass@k from pass@k campaign (temp=0.7, n=3 per task)
- Overall 19.0% at temp=0.7 vs 35.4% primary at temp=0.0
- Acknowledge n=3 power limitation explicitly

**S6.8 Statistical Summary:**
- Table 13: all test statistics

### B.2 Fill S7 Discussion Sections

**S7.3 Model Capability:**
- Single-model Qwen 3.5 analysis (35.4%, MoE architecture)
- Leave Gemini placeholder

**S7.4 Direction Asymmetry:**
- No statistically significant asymmetry
- But failure MODE differs by direction (the interesting finding)
- cuda-to-omp: BUILD_FAIL dominant → model struggles with OMP pragma synthesis
- cuda-to-opencl: RUN_FAIL dominant → OpenCL JIT catches runtime errors
- opencl-to-cuda: BUILD_FAIL dominant → model can't generate valid CUDA from OpenCL

**S7.5 Augmentation Robustness (REWRITTEN — null result):**
- Cochran-Armitage null → no monotonic trend
- Against memorization hypothesis
- Against augmentation-as-data-augmentation hypothesis
- Model failures are structural, not surface-level

### B.3 Fix Known Inconsistencies

- **B2:** Augmentation baseline → "68 of 88 non-KNOWN_FAIL"
- **B3:** Task count → 480 primary + 426 pass@k, explain 710 plan vs actual
- **S1.3:** Verify contribution counts
- **Table 5:** Update for Qwen 3.5 + Gemini placeholder
- **Remove archived pilot data** (lines 674-709)
- **Abstract:** Fill with primary campaign numbers (Gemini remains [PENDING])

### B.4 Acknowledge Power Limitations (S7 or S8)

Add explicit acknowledgment of:
1. n=16 balanced subset for augmentation trend test
2. n=3 per task for pass@k (very low power)
3. Single model (cannot generalize)
4. 96 L0 tasks across 6 directions → wide CIs per direction

---

## Acceptance Criteria

- [ ] 7 mislabeled results fixed on disk
- [ ] generate_paper_data.py written, tested, produces paper_data.json
- [ ] paper_data.json verified against raw file counts
- [ ] Zero [PENDING] in S6 (except Gemini-specific cells)
- [ ] S7.3-S7.5 have Qwen analysis (with Gemini placeholders)
- [ ] S6.5/S7.5 rewritten around augmentation null result
- [ ] B2, B3, S1.3, Table 5 fixed
- [ ] Archived pilot data removed
- [ ] Abstract updated with primary campaign numbers
- [ ] Power limitations acknowledged in S7/S8
- [ ] At least 2 findings log insights inline with data citations

---

## Key Files

| File | Purpose | Action |
|------|---------|--------|
| `scripts/analysis/generate_paper_data.py` | New analysis script | WRITE |
| `results/analysis/paper_data.json` | Clean data for paper | GENERATED |
| `docs/paper/paper_draft.md` | Main paper | EDIT: fill S6/S7 |
| `docs/paper/drafts/eval_findings_log.md` | Findings | READ: extract insights |
| `results/evaluation/together-qwen-3.5-397b-a17b/` | Raw results | READ + FIX 7 files |
| `scripts/analysis/build_error_taxonomy.py` | Error classification regexes | READ: reuse patterns |
| `scripts/analysis/statistical_analysis.py` | Statistical functions | READ: reuse Cochran-Armitage, McNemar |
