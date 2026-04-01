# Pre-Built Scenario Templates

Use with `/agent-team --scenario <name>`. Skips Phase 2 (team design) and provides
a pre-filled team configuration. Still requires Samyak's approval before launching.

**Dynamic model directories:** Scenarios referencing model results use `{model-N}`
placeholders. At launch time, list `results/evaluation/` to discover current model
directories and fill them in. Never hardcode model directory names.

---

## `multi-model-eval`

**Purpose:** Deep-dive comparison across model result directories.

| Teammate | Role | Scope |
|----------|------|-------|
| `{model-1}-analyst` | Results analyst | `results/evaluation/{model-1}/` |
| `{model-2}-analyst` | Results analyst | `results/evaluation/{model-2}/` |
| `{model-3}-analyst` | Results analyst | `results/evaluation/{model-3}/` |
| comparator | Cross-model comparator | Analyst summaries only (no raw file reads) |

**Per-analyst:** Delegate reads to Explore subagent. Extract: `overall_status`,
`build_error_snippet`, `run_stderr_snippet`, `attempts[]`, `model_id`, `direction`,
`tokens_used`. Compute: pass rate by direction, per-kernel failures, self-repair stats.

**Comparator:** Compute deltas, identify per-kernel anomalies, rank by direction.
Works ONLY from analyst summaries — never reads result files directly.

**Cost:** ~4x

---

## `paper-assembly`

**Purpose:** Parallel data gathering for SC26 paper section drafting.

| Teammate | Role | Scope |
|----------|------|-------|
| data-processor | Eval data processor | `results/evaluation/` (delegate per-model to subagents) |
| lit-reviewer | Related work searcher | WebSearch + `docs/` |
| methods-reader | Methodology documenter | `c_augmentation/`, `results/augmentation/` |

**data-processor:** Extract `overall_status`, `direction`, `kernel_name`, `attempts[]`.
Build pass rates, failure taxonomy, per-kernel tiers, direction asymmetry as markdown tables.

**lit-reviewer:** Search: SWE-bench, HumanEval, TransCoder, LASSI, CodeRosetta,
HPC-Coder-v2, OMPify, HPCorpus. Differentiate each from ParBench.

**methods-reader:** Document augmentation methodology, transform catalog,
level-invariance evidence, harness pipeline stages.

**Cost:** ~3x

---

## `failure-investigation`

**Purpose:** Multi-stage pipeline debugging for a specific kernel failure.

**Usage:** `/agent-team --scenario failure-investigation "rodinia-hotspot-omp VERIFY_FAIL"`

| Teammate | Role | Scope |
|----------|------|-------|
| build-investigator | Build stage analyst | `harness/builder.py`, spec `build` section, source Makefiles |
| run-investigator | Run stage analyst | `harness/runner.py`, spec `run` section, source argc parsing |
| verify-investigator | Verify stage analyst | `harness/verifier.py`, spec `verify` section, reference output |

Each investigator: Grep for relevant functions first, read only their stage,
share findings to identify the failing stage.

**Cost:** ~3x

---

## `cross-model-taxonomy`

**Purpose:** Build unified failure taxonomy table across all models for the paper.

| Teammate | Role | Scope |
|----------|------|-------|
| `{model-1}-classifier` | Failure classifier | `results/evaluation/{model-1}/` |
| `{model-2}-classifier` | Failure classifier | `results/evaluation/{model-2}/` |
| `{model-3}-classifier` | Failure classifier | `results/evaluation/{model-3}/` |
| taxonomy-synthesizer | Synthesizer | Classifier summaries only |

**Per-classifier:** Delegate reads to Explore subagent. Extract: `overall_status`,
`build_error_snippet`, `run_stderr_snippet`, `direction`, `kernel_name`.
Classify non-PASS by: error category, root cause, affected kernels.

**Synthesizer:** Merge per-model classifications into unified taxonomy table.

**Cost:** ~4x

---

## `post-batch-analysis`

**Purpose:** Parallel post-eval analysis after a batch completes.

| Teammate | Role | Scope |
|----------|------|-------|
| analyzer | Eval summary generator | `scripts/evaluation/analyze_eval.py`, `results/evaluation/` |
| classifier | Translation classifier | `scripts/evaluation/classify_translation_pairs.py` |
| viz-refresher | Dashboard refresher | `scripts/generate_viz_data.py`, `visualizations/` |

**Cost:** ~3x

---

## `augmentation-audit`

**Purpose:** Verify augmentation level-invariance claim against actual data.

| Teammate | Role | Scope |
|----------|------|-------|
| phase3-reader | Phase 3 results | `results/augmentation/phase3_*.json` |
| phase4-reader | Phase 4 results | `results/augmentation/phase4_*.json` |
| phase5-reader | Phase 5 + full results | `results/augmentation/phase5_*.json`, `full_aug_results.json` |
| retest-reader | Retest results | `results/augmentation/retest_*.json` |

After all readers report, lead verifies: 54/60 Rodinia PASS at all L1-L4,
6 KNOWN_FAIL excluded.

**Cost:** ~4x

---

## Creating Custom Scenarios

Not every task fits a pre-built template. Use Phase 2 (team design) for custom teams.
The templates above are starting points — adapt teammate count, scope, and roles to
match the actual task.
