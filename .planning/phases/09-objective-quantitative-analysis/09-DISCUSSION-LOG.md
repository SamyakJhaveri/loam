# Phase 9: Objective Quantitative Analysis - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 09-objective-quantitative-analysis
**Areas discussed:** Script architecture, Output structure & provenance, Statistical completions, Validation & spot-checks

---

## Script Architecture

| Option | Description | Selected |
|--------|-------------|----------|
| Aggregator | Reads existing analysis JSONs, computes only new metrics | |
| Standalone recompute | Reads raw result JSONs directly, recomputes everything | ✓ (with Claude discretion on avoiding duplication) |
| You decide | Claude picks | |

**User's choice:** Standalone from raw result JSONs. Claude decides which metrics to compute fresh vs pull from existing to avoid duplication.
**Notes:** User emphasized raw JSONs as ground truth.

| Option | Description | Selected |
|--------|-------------|----------|
| Single file | One quantitative_findings.py | ✓ |
| Multi-module | Orchestrator + separate modules | |

**User's choice:** Single file — consistent with Phase 2 and Phase 3 patterns.

| Option | Description | Selected |
|--------|-------------|----------|
| Standard estimator (Chen et al.) | Unbiased pass@k estimator | |
| Simple fraction | Fraction of seeds passing (0/3, 1/3, 2/3, 3/3) | ✓ |

**User's choice:** Simple fraction. No extrapolation beyond k=3.

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, compare & warn | Compute from raw, then cross-check vs existing | ✓ |
| No, raw only | Pure raw computation | |

**User's choice:** Cross-check against existing analysis JSONs, warn on discrepancies >0.1%.

| Option | Description | Selected |
|--------|-------------|----------|
| Full 1,248 dataset | All 5 suites with per-suite breakdowns | ✓ |
| Rodinia-primary | Rodinia primary, others supplementary | |

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude by default | Auto-exclude 8 KNOWN_FAIL | ✓ |
| Include with flag | Include all, tag KNOWN_FAIL | |

| Option | Description | Selected |
|--------|-------------|----------|
| Separate section | omp_target in case-study section | ✓ |
| Exclude entirely | Drop omp_target | |
| Mix in with standard | Treat as standard direction | |

| Option | Description | Selected |
|--------|-------------|----------|
| Quiet with summary | Final summary line, -v for verbose | ✓ |
| Verbose by default | Print progress per dimension | |

### Campaign Distinction (User-initiated)

**User explained:** Two separate eval campaigns ran. Must be treated as separate:
- Campaign 1: All benchmarks, L0-L4, 3 retries, temp=0.0, 1 sample
- Campaign 2: All benchmarks, L0 only, 1 try, temp=0.7, 3 samples (pass@k, k=3)
- Distinguished by `-s{N}` filename suffix (Campaign 2) vs no suffix/-L{N} (Campaign 1)

| Option | Description | Selected |
|--------|-------------|----------|
| Split by nature | Campaign 1 → 12 dims, Campaign 2 → pass@k | |
| Both feed everything | All 14 dims for both | |
| You decide | Claude maps based on analytical sense | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| No filter, full dataset | Full dataset, per-suite breakdowns | ✓ |
| Configurable --suite | Optional --suite flag | |

| Option | Description | Selected |
|--------|-------------|----------|
| Per-direction + per-suite | Full breakdowns for Campaign 2 | ✓ |
| Aggregate only | Just overall pass@k | |

| Option | Description | Selected |
|--------|-------------|----------|
| Read existing | SLoC from benchmark_characterization.json | ✓ |
| Recompute from source | Re-run cloc on source files | |

---

## Output Structure & Provenance

| Option | Description | Selected |
|--------|-------------|----------|
| Campaign-first | metadata, campaign_1, campaign_2, cross_checks | ✓ |
| Dimension-first | Top keys = 14 dimensions | |

| Option | Description | Selected |
|--------|-------------|----------|
| Source path + field | value, source, files_matched, derivation | ✓ |
| Full JSON pointer | Exact paths to contributing raw files | |
| Minimal | Just value + description | |

| Option | Description | Selected |
|--------|-------------|----------|
| Paper-ready tables | Copy-pasteable tables per dimension | ✓ |
| Summary with pointers | Concise summary + JSON refs | |

| Option | Description | Selected |
|--------|-------------|----------|
| Separate fields | value, ci_lower, ci_upper, ci_level | ✓ |
| Pre-formatted strings | "36.2% [32.1%, 40.6%]" | |
| Both | Structured + display string | |

| Option | Description | Selected |
|--------|-------------|----------|
| Separate sections | Campaign 1 then Campaign 2 in MD | ✓ |
| By dimension | Interleaved by dimension | |

| Option | Description | Selected |
|--------|-------------|----------|
| results/analysis/ | Both files in results/analysis/ | ✓ |
| docs/paper/analysis/ | Paper-specific location | |
| Both locations | JSON in results, MD in docs | |

| Option | Description | Selected |
|--------|-------------|----------|
| No cross-comparison | Campaigns stay separate | ✓ |
| Explicit comparison | Compare C1 L0 vs C2 pass@1 | |

| Option | Description | Selected |
|--------|-------------|----------|
| By pass rate | Ordered by pass rate for tier visibility | ✓ |
| Alphabetical | Simple stable ordering | |
| By suite then alpha | Group by suite | |

| Option | Description | Selected |
|--------|-------------|----------|
| Brief observations | 1-line highlights after each table | ✓ |
| Raw data only | Just tables | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, claim mapping | paper_claims section mapping to JSON fields | ✓ |
| No, separate concern | Phase 11's job | |

| Option | Description | Selected |
|--------|-------------|----------|
| Decimals 0-1 | 0.362 internally | ✓ |
| Percentage integers | 36.2 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Category counts + top errors | Top-level + top-3 build subcategories | ✓ |
| Just top-level | 4 failure types only | |
| Full taxonomy tree | Complete hierarchy | |

| Option | Description | Selected |
|--------|-------------|----------|
| From raw attempts | Compute from attempts[] arrays | ✓ |
| Read existing analysis | Pull from selfrepair_analysis.json | |

---

## Statistical Completions

| Option | Description | Selected |
|--------|-------------|----------|
| From raw paired data | Build paired vectors, compute McNemar | ✓ |
| Read existing stats | Pull from statistical_analysis.json | |

| Option | Description | Selected |
|--------|-------------|----------|
| From spec JSON fields | Derive complexity from translation_targets/prompt_payload | ✓ |
| Read existing classification | Pull from benchmark_characterization.json | |

| Option | Description | Selected |
|--------|-------------|----------|
| Both Spearman + Pearson | | |
| Spearman only | | |
| You decide | Claude picks | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| X-to-OpenCL vs X-to-OMP | Compare kernel-only vs full program | ✓ |
| Paired kernel comparison | Matched pairs per kernel | |

| Option | Description | Selected |
|--------|-------------|----------|
| Stick to the 14 | Exactly roadmap dimensions | ✓ |
| Add effect sizes everywhere | Cohen's h, Cramer's V | |

| Option | Description | Selected |
|--------|-------------|----------|
| 95% | Standard Wilson CIs | ✓ |
| Both 95% and 99% | | |

| Option | Description | Selected |
|--------|-------------|----------|
| All directions | CA test per direction + aggregate | ✓ |
| cuda-to-omp primary only | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Quartile-based | Rank by L0 pass rate, split quartiles | ✓ |
| Threshold-based | Hard-coded Easy/Medium/Hard cutoffs | |

| Option | Description | Selected |
|--------|-------------|----------|
| Qwen API pricing | Together AI rate, stored as constants | ✓ |
| Multiple model pricing | Qwen + reference rates | |

---

## Validation & Spot-Checks

| Option | Description | Selected |
|--------|-------------|----------|
| Automated assertions | --validate flag, PASS/FAIL per check | ✓ |
| Manual jq spot-checks | Separate shell script | |

| Option | Description | Selected |
|--------|-------------|----------|
| Critical paper claims | Overall rate, per-suite, file counts, direction extremes, BUILD_FAIL | ✓ |
| One per dimension | Representative number per dimension | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, include cross-check | --validate also runs cross-check comparison | ✓ |
| Separate concerns | Cross-check during main run only | |

| Option | Description | Selected |
|--------|-------------|----------|
| Both | Stdout + quantitative_findings_validation.json | ✓ |
| Print only | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Warn only | Discrepancies are warnings, never failures | ✓ |
| Fail on >1% | Hard fail on significant divergence | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, pre-audit | Parse paper.tex, compare vs paper_claims | ✓ |
| No, Phase 11's job | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, sanity checks | CI ordering, weighted averages, no NaN/null | ✓ |
| No, data integrity only | | |

| Option | Description | Selected |
|--------|-------------|----------|
| No, not needed | Script is deterministic | ✓ |
| Yes, for safety | --dry-run for preview | |

---

## Claude's Discretion

- JSON metadata content (reproducibility info)
- SLoC correlation method selection (Spearman vs Pearson vs both)
- Dimension-to-campaign mapping for edge cases
- Per-kernel ordering direction (ascending vs descending)
- Specific spot-check targets within "critical paper claims"
- Complexity classification edge cases

## Deferred Ideas

None — discussion stayed within phase scope.
