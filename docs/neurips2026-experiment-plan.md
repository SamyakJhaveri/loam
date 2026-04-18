# ParBench NeurIPS 2026 — Experiment Plan

**Author:** Samyak Jhaveri · **Reviewers:** Gal Oren, Niranjan Hasabnis, Le Chen, Tomer Bitan
**Target:** NeurIPS 2026 Datasets & Benchmarks · **Deadline:** May 1, 2026
**Status:** Approved with revisions by Gal 2026-04-16; confirmed by Samyak 2026-04-16. See §2.4 for the authoritative current design.
**Pre-approval snapshot:** `~/.claude/plans/gsd-context-goal-i-cached-finch.md` (unmodified historical record).

> **⚠️ AUTHORITATIVE DESIGN LIVES IN §2.4 BELOW.** §§1–2.3 and §§3–9 are the pre-approval draft. They remain here for traceability but are superseded anywhere §2.4 conflicts.

---

## 1. Executive summary

ParBench measures LLMs on parallel-code translation across **6 directions** (OpenMP ↔ OpenCL ↔ CUDA) over **87 executable kernels** spanning 5 benchmark suites. This document replaces the previous two-campaign design, which confounded temperature, augmentation, sampling, and self-repair in a single run, with **one canonical experiment + one clean ablation study** isolating source-code robustness. Total estimated cost: **~$843** on GPT-5 standard tier + Together AI Qwen, total wall clock **~1.5 days** with parallel-stream execution across 2+ machines. All infrastructure already exists — changes are additive.

## 2. Experimental design

### 2.1 Canonical experiment — headline pass@3 result

The single number the paper will anchor every claim around.

| Parameter | Value | Rationale |
|---|---|---|
| Sampling | **pass@3 at temperature = 0.7** | Meeting-agreed Apr 15. Standard practice in parallel-code literature (ParEval, HPC-Coder-v2) for sampling-based evaluation. |
| Reasoning | **Thinking ON** (both models) | Meeting-agreed. Reflects "best the model can do" under test-time compute scaling. |
| Self-repair | **OFF** (max_retries=1) | Isolates one-shot capability; retries introduce confound between LLM ability and error-signal quality. |
| Augmentation | **L0 only** (no source perturbation) | Measures model capability on canonical source. Robustness is the ablation axis. |
| Models | **together-qwen-3.5-397b-a17b** (open) + **azure-gpt-5** w/ reasoning_effort=medium (proprietary) | Per meeting: two-track open-source + proprietary story. |
| Kernels | All **87 TRUE PASS** (54 Rodinia + 3 XSBench + 4 RSBench + 3 mixbench + 23 HeCBench curated). Excludes 8 KNOWN_FAIL. | Meeting: keep ~100 for statistical coverage. |
| Directions | All **6** (cuda↔omp, cuda↔opencl, omp↔opencl) | Fixed across every experiment. |

**Samples per canonical run:** 87 kernels × 6 directions × 3 samples × 2 models = **3,132 samples total**.

### 2.2 Ablation study — source-robustness L1 through L4

One cleanly isolated variable: the semantics-preserving AST perturbation level applied to source before translation.

| Parameter | Value | Changed from canonical? |
|---|---|---|
| Sampling | **pass@1 at temperature = 0.7** | Yes — reduces compute 3× |
| Reasoning | Thinking ON | No (held constant) |
| Self-repair | OFF (max_retries=1) | No |
| Augmentation | **L1, L2, L3, L4** (4 separate runs) | Yes — this is the ablation axis |
| Models | Both (Qwen + GPT-5 w/ thinking) | No |
| Kernels | All 87 | No |
| Directions | All 6 | No |

**Samples per ablation run:** 87 × 6 × 1 × 4 levels × 2 models = **4,176 samples total**.

**Research question:** For each perturbation intensity L_k ∈ {1,2,3,4}, what fraction of (kernel, direction) cells that pass at L0 fail at L_k, and vice versa? → characterizes how robust each model is to semantics-preserving source changes.

### 2.3 Methodological note on mixed estimators (important for reviewer defense)

**Concern:** Canonical reports pass@3, ablation reports pass@1. Naïvely comparing them is unsound — pass@3 ≥ pass@1 always.

**Resolution (no extra compute):** Because the canonical run collects 3 independent samples per (kernel, direction, model) cell, we can **derive pass@1 from the first canonical sample** and compare it directly to the ablation's pass@1. This gives:

- **Canonical headline:** pass@3 at L0 (best-effort performance)
- **Canonical apples-to-apples baseline:** pass@1 at L0 (from first sample of canonical run)
- **Ablation:** pass@1 at L1, L2, L3, L4
- **Robustness metric:** Δpass@1(L_k) = pass@1_canonical − pass@1_L_k

No extra sampling needed. We already have the data implicit in the canonical pass@3 run.

### 2.4 Gal-approved revisions (2026-04-16) — AUTHORITATIVE

Gal reviewed the §2.1–2.3 draft on 2026-04-16 and approved with one budget-driven change: **the GPT ablation becomes L0-conditional.** Samyak confirmed specific parameters the same day. This section supersedes §2.2 wherever they conflict.

**What stays identical to §2.1 (canonical):**
- pass@3, L0, temp=0.7, thinking=ON, reasoning_effort=medium, self-repair=OFF
- All 87 TRUE PASS kernels × 6 directions (+ omp_target case studies for XSBench/RSBench where available)
- Both models: `together-qwen-3.5-397b-a17b` + `azure-gpt-5.3-chat` (renamed from "azure-gpt-5" to reflect the specific deployment slot)

> ⚠️ **`azure-gpt-5.3-chat` is a placeholder identifier — NOT yet runnable.** Verified 2026-04-16 against `scripts/evaluation/llm_evaluate.py` (MODEL_REGISTRY, lines 61–125): only `azure-gpt-4.1` is registered; no GPT-5 variant exists. Two things must land before Phase A launches: (1) Task 7 (§2.4 code-change table row 1) registers the model entry, and (2) Le confirms the exact Azure deployment name + TPM quota. Treat "GPT-5.3 Chat" throughout this document as a working identifier, not a resolved one.

**What changes for the ablation (supersedes §2.2):**

| Parameter | §2.2 (pre-approval) | §2.4 (authoritative) |
|---|---|---|
| Filter | None — all 87 × 6 cells | **pass@1-of-any from canonical** (cell included iff ≥1 of 3 canonical samples passed at L0) |
| Levels | L1, L2, L3, L4 (all 4) | **L1, L2, L3, L4 on ALL L0-passers** (no subset, no middle-level-only sampling) |
| Audit sample | N/A | **None.** Paper threats-to-validity will acknowledge L0-failers were not evaluated under perturbation |
| Symmetry | Both models run full 87 × 6 | **Both models run the same filter** for apples-to-apples delta |
| Launch | Parallel with canonical | **Serial after canonical** — ablation depends on canonical passer-set derivation |

**Estimator-denominator clarification (supersedes §2.3 where applicable):** Because the ablation runs only on L0-passer cells, Δpass@1(L_k) must be computed with both terms restricted to the same L0-passer cell set (per model). Specifically: `pass@1_canonical` in §2.3's Δ formula is derived from the first canonical sample **of each L0-passer cell only** — NOT from the full 87 × 6 canonical run. Aggregate robustness numbers must report this denominator (≈287 cells per model at the 55% midpoint). Per-cell Δ within the L0-passer set is the primary robustness statistic; an overall robustness rate on the full 87 × 6 is not directly computable without an audit sample of L0-failers (see "No audit sample" row above).

**Budget (revised from §3.2):**

Assuming 55% canonical L0-pass rate (pass@1-of-any; range 45–65%, linear scaling):

> ⚠️ **The 55% figure is a working assumption, not a measurement.** Closest in-repo datapoint is Qwen historical first-sample pass rate ≈31% (347/1120 non-KNOWN_FAIL, `known-issues.md` Pipeline Audit 2026-04-09). Pass@1-of-any on 3-sample pass@3 runs will exceed 31% because "any of 3 passes" is strictly more permissive than "first sample passes," but 55% is an extrapolation, not an observation. The GPT-5-class L0-pass prior is cited from general literature, not from an in-repo run. Final coverage — and therefore the final budget — is only knowable after Phase A completes and `derive_l0_passers.py` runs against real result JSONs.

| Stream | Samples | GPT | Qwen |
|---|---:|---:|---:|
| qwen_canonical (unchanged) | 1,566 | — | $39 |
| gpt_canonical (unchanged) | 1,566 | $322 | — |
| qwen_ablation (287 cells × 4 levels) | 1,148 | — | $29 |
| gpt_ablation (287 cells × 4 levels) | 1,148 | $237 | — |
| **TOTAL (estimated)** | **5,428** | **$559** | **$68** |

**Grand total ≈ $627** (26% savings vs pre-approval $843) at the 55% midpoint. Sensitivity to L0-pass rate (linear in passer count): at 45% GPT ≈ **$516**, at 65% GPT ≈ **$602** (Qwen $55–$80 over the same range). **GPT side $559 (midpoint) overshoots Gal's $400 target by ~$116–$202 depending on realized pass rate ($159 at midpoint, 40%).** **Samyak accepted this tradeoff on 2026-04-16 to preserve the full L1→L4 degradation curve (reviewer value: can report monotonic degradation across all levels, not just outer endpoints). "Accepted" here refers to Samyak's scope choice, not a bilateral budget agreement — Gal's sign-off on the overshoot is still PENDING. Do NOT launch Phase A until Gal's sign-off is documented.** Fallback if Gal declines: raise filter to pass@2-of-3 (≈22% pass rate — also an assumption, not measured → ~$94 GPT ablation → $416 GPT total, hits target).

**Threats-to-validity commitment (TODO, not done):** The "No audit sample" row above promises that the paper's threats-to-validity section will acknowledge L0-failers were not evaluated under perturbation. That section has **not been written yet** — it is an outstanding Phase 4 deliverable. Tracking: if Phase 4 does not produce that subsection, this mitigation argument is incomplete regardless of what §2.4 states.

**Launch sequence (supersedes §4):**

Three-phase execution because ablation is data-dependent on canonical output:

1. **Phase A — Canonical (Apr 19)**: 2 parallel streams on 2 machines, ~17h wall clock each.
2. **Phase B — Derive (Apr 20 AM, ~1h)**: `derive_l0_passers.py` produces `l0_passers_{qwen,gpt5}.json`, committed to `.planning/eval-selections/`.
3. **Phase C — Ablation (Apr 20 PM, ~4-5h)**: 2 parallel streams consuming passer JSONs via new `--task-list` flag on `run_eval_batch.py`.

Net wall clock across Apr 19–20 is ~20–22h (vs ~17h in §4 parallel-all-streams design). Still fits May 1 deadline with ≥5-day buffer for analysis + paper.

**Code changes required (supersedes §5):**

| # | Change | File | Status |
|---|---|---|---|
| 1 | Add `azure-gpt-5.3-chat` entry to `MODEL_REGISTRY` (use `azure-gpt-4.1` at line 94 as the structural template) | `scripts/evaluation/llm_evaluate.py` (MODEL_REGISTRY dict starts line 61; azure-gpt-4.1 entry at line 94 — insert new entry nearby) | Pending execution |
| 2 | Add `reasoning_effort="medium"` on the **Azure** `client_az.chat.completions.create(...)` call (guarded by capability check — only for reasoning-capable models like gpt-5.4, o3). NOTE: line 956's `reasoning_effort="none"` is in the **Gemini** path, not Azure — do NOT edit that one. | `scripts/evaluation/llm_evaluate.py:878–883` (Azure call block; add parameter between `messages=` and closing `)`) | Pending |
| 3 | Flip Qwen `enable_thinking: False → True`; add `--thinking on\|off` CLI flag | `scripts/evaluation/llm_evaluate.py:1001` | Pending |
| 4 | Remove `gpt-4.1-2025-04-14` + `azure-gpt-4.1` + `gpt-4.1-mini` from scripts/docs | 10 files (see §Appendix B) | Pending |
| 5 | New `derive_l0_passers.py` — emit `l0_passers_{model}.json` (pass@1-of-any filter) | `scripts/evaluation/derive_l0_passers.py` | Pending |
| 6 | Add `--task-list <json>` flag to `run_eval_batch.py` | `scripts/evaluation/run_eval_batch.py` | Pending |

> Line numbers verified against current `llm_evaluate.py` (2099 lines total) on 2026-04-16. Re-verify before execution if significant edits land in the interim.

**Decisions deferred vs §9:**
- **Item 1 (GPT-5 tier)**: Gal approved standard via the budget-cutting directive.
- **Item 3 (Option D)**: Approved with revision (L0-conditional ablation per §2.4).
- **Item 4 (gpt-4.1-mini purge)**: Approved by Samyak 2026-04-16 — result JSONs on disk stay, scripts/docs get purged.
- **Item 2 (Azure quota)**: Still pending Le; required before Phase A.
- **Item 5 (2-machine allocation)**: Still pending; if only 1 machine available, fallback is serial canonical (+17h wall clock, still fits).

## 3. Grounded cost + wall-clock

### 3.1 Per-sample token economics

Based on 50-sample empirical measurement of existing Qwen results (thinking OFF): median prompt = 1,976 tokens, median completion = 1,782 tokens, max completion = 8,706 tokens. With thinking ON, completion tokens scale ~5–10× (reasoning tokens billed as output). Conservative per-sample estimates below use **5k prompt + 20k completion**:

| Model | Per-sample cost | Source |
|---|---:|---|
| GPT-5 standard (reasoning_effort=medium) | **$0.3125** | $2.50/M in + $15/M out (Azure, <272K context) [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/azure-openai/), verified 2026-04-17 |
| GPT-5 Pro (reasoning-heavy) | $2.480 | $15/M in + $120/M out |
| o3 standard (alternative) | $0.170 | $2/M in + $8/M out |
| Qwen 3.5 397B via Together AI | **$0.075** | $0.60/M in + $3.60/M out [Together pricing](https://www.together.ai/models/qwen3-5-397b-a17b), verified 2026-04-17 |

> **2026-04-17 pricing refresh.** Azure GPT-5 standard was previously cited at $1.25/M in + $10/M out ($0.206/sample); the authoritative rate is now $2.50/M in + $15/M out ($0.3125/sample) per the Azure pricing page for GPT-5 deployments below the 272K context threshold (Batch API is $1.25/M in + $7.50/M out). Together's Qwen 3.5 397B rate was previously estimated at ~$1/M in + $2/M out ($0.025/sample); the advertised rate is $0.60/M in + $3.60/M out ($0.075/sample). The §3.2 table below still reflects the OLD rates AND the pre-2026-04-16 two-campaign scope (superseded by §2.4's canonical + L0-conditional ablation design). The authoritative current cost model is `.planning/phases/02-llm-eval-testing/02-CONTEXT.md` D-30; see also `.planning/phases/02-llm-eval-testing/02-08-integration-smoke-and-handoff-PLAN.md`. Gal signed off on the $559 GPT overshoot on 2026-04-17 (at old pricing); a recomputation at the new $0.3125/sample rate lands the canonical + ablation GPT spend closer to ~$848 — deviations from the original $559 will be flagged if/when they materialize, per Samyak's standing instruction "if anything changes I will let you know."

### 3.2 Full experiment budget (GPT-5 standard tier — OLD rates, two-campaign scope, SUPERSEDED)

| Stream | Samples | GPT-5 std | Qwen | Stream total |
|---|---:|---:|---:|---:|
| qwen_canonical (L0, pass@3) | 1,566 | — | $39 | $39 |
| gpt_canonical (L0, pass@3) | 1,566 | $322 | — | $322 |
| qwen_ablation (L1–L4, pass@1) | 2,088 | — | $52 | $52 |
| gpt_ablation (L1–L4, pass@1) | 2,088 | $430 | — | $430 |
| **TOTAL** | **7,308** | **$752** | **$91** | **$843** |

GPT-5 Pro tier would multiply to **~$9,030**. Unless Azure credits cover it, we recommend standard tier.

### 3.3 Wall-clock with parallel streams

Assumptions: ~5 min/task (3 LLM calls at ~1 min each with thinking + ~30–60s harness build/run/verify), 10-way task concurrency per machine, no major rate-limit throttling.

| Stream | Samples | Tasks/hour (10-way) | Wall clock |
|---|---:|---:|---:|
| qwen_canonical | 522 | 120 | 4.4 h |
| qwen_ablation | 2,088 | 120 | 17.4 h |
| gpt_canonical | 522 | 120 | 4.4 h |
| gpt_ablation | 2,088 | 120 | 17.4 h |

(522 = 1,566 samples / 3 pass@k samples per task; each task runs 3 LLM calls sequentially or concurrently depending on concurrency strategy.)

**If 4 streams run in parallel on 2+ machines: longest stream dominates → ~17–18 hours wall clock, ~1 day total.**
**If 2 streams run in parallel (one machine per model, canonical then ablation): ~22 hours per model → ~1 day both complete.**

Either way, fits comfortably in the May 1 deadline with retry budget.

## 4. Parallelization plan — four independent streams

Each stream is fully independent (no shared files mutated, no ordering dependency). Distribute across available machines:

| Stream name | Command template | Output prefix |
|---|---|---|
| `qwen_main` | `run_eval_batch.py --models together-qwen-3.5-397b-a17b --temperature 0.7 --num-samples 3 --augment-levels 0 --max-retries 1 --direction <D>` | `results/evaluation/qwen_main/` |
| `qwen_abl` | same as above, but `--augment-levels 1 2 3 4 --num-samples 1` | `results/evaluation/qwen_abl/` |
| `gpt_main` | `run_eval_batch.py --models azure-gpt-5 --temperature 0.7 --num-samples 3 --augment-levels 0 --max-retries 1 --direction <D>` | `results/evaluation/gpt_main/` |
| `gpt_abl` | same as above, but `--augment-levels 1 2 3 4 --num-samples 1` | `results/evaluation/gpt_abl/` |

Each stream runs all 6 directions (can be a second for-loop over `--direction` inside the stream's tmux session). `--resume` works per-stream so interruptions are safe.

## 5. Required ParBench code changes

All changes additive. No existing result JSONs touched. No pipeline redesign.

| # | Change | File | Status |
|---|---|---|---|
| 1 | Add `azure-gpt-5` entry to `MODEL_REGISTRY` (provider=azure, deployment name TBD by Le) | `scripts/evaluation/llm_evaluate.py:94` | Required |
| 2 | Add `reasoning_effort="medium"` param in Azure API call for reasoning-capable models | `scripts/evaluation/llm_evaluate.py:879` | Required |
| 3 | Flip Qwen `enable_thinking: False` → `True` (or add `--thinking on\|off` CLI flag for future ablation) | `scripts/evaluation/llm_evaluate.py:1001` | Required |
| 4 | Remove `gpt-4.1-2025-04-14` and `azure-gpt-4.1` entries from `MODEL_REGISTRY` (per user directive: "remove gpt-4.1 from scripts, memory, agenda") | `scripts/evaluation/llm_evaluate.py:82–100` | Required |
| 5 | Remove `gpt-4.1-mini` references from 14 files (analysis scripts, batch scripts, docs) | see Appendix B | Required |
| 6 | Per-stream output prefix convention documented in `scripts/batch/run_eval_campaign.sh` | `scripts/batch/` | Nice-to-have |
| 7 | Archive old `qwen_hecbench` / `qwen_small` tmux sessions | host machine | Cleanup |

**Zero changes needed to:** harness (build/run/verify logic), augmentation engine (L0–L4 already deterministic seed=42+level), pass@k estimator (`statistical_analysis.py:706` already uses Chen et al. 2021 unbiased form), result schema, manifest, spec JSONs.

## 6. Metrics reported in the paper

All derived from existing result-JSON schema without new instrumentation:

| Metric | From field | Reported where |
|---|---|---|
| pass@3, pass@1 at L0 | `overall_status=="PASS"` counts | Main result table |
| pass@1 at L1, L2, L3, L4 | same, filtered by `augment_level` | Robustness section |
| Δpass@1(L_k) = pass@1_canonical − pass@1_L_k | derived | Robustness figure |
| Pass rate by direction × model | `by_direction[...]` | Per-direction breakdown |
| Pass rate by suite × model | `by_kernel[...]` + suite mapping | Coverage table |
| Failure taxonomy (BUILD/RUN/VERIFY/EXTRACTION) | `overall_status` breakdown | Error analysis |
| Prompt + completion tokens per task | `prompt_tokens`, `completion_tokens` | Efficiency discussion |
| Seed variance at canonical | std of 3 pass@3 samples | Reproducibility paragraph |

**Not reported (honest limitations, to be stated in the paper):**
- **Speedup / parallel efficiency:** schema has `speedup_ratio` field but wall-clock baselines are sub-millisecond on many kernels, making ratios noise-dominated. Instrumented kernel timing is deferred to follow-up work.
- **Code similarity (CrystalBLEU, CodeBLEU):** not currently computed; optional post-hoc analysis from stored `translated_files` if bandwidth allows before deadline.

## 7. Risks + mitigation

| Risk | Likelihood | Mitigation |
|---|---|---|
| Azure quota/rate-limit throttling on GPT-5 thinking | Medium — depends on Le's subscription tier | Confirm TPM/RPM quota with Le before launch; fall back to `o3` if cheaper and equivalent |
| Thinking tokens > 20k average → cost overrun | Low-Medium | Budget monitored daily via `analyze_eval.py --tokens`; abort if 50% over projection |
| Model API outage mid-run | Low | `--resume` flag re-runs only missing task result files; no loss |
| New build failures under augmentation | Known — existing augmentation verify data shows ~10% baseline failure at L3/L4 | Report as part of the robustness story; expected signal |
| Reviewer pushback on mixed pass@3 / pass@1 estimators | Addressed | Paper explicitly reports both canonical pass@3 and pass@1 from first sample; ablation delta is computed at matched pass@1 |

## 8. Timeline to May 1

| Date | Milestone | Who |
|---|---|---|
| Apr 17 (Thu) | Gal approves this plan; Le confirms Azure quota | Gal, Le |
| Apr 18 (Fri) | Code changes #1–#4 committed + tested on 1 kernel per suite | Samyak |
| Apr 19 (Sat) | 4 streams launch in parallel on 2+ machines | Samyak + Le |
| Apr 20–21 | Streams complete (~1 day wall clock + buffer) | — |
| Apr 22 (Tue) | Analysis: `analyze_eval.py` regenerated; paper figures drafted | Samyak |
| Apr 23–27 | Paper rewrite: `docs/paper/latex/overleaf_main.tex` sections updated with new numbers | Samyak + reviewers |
| Apr 28–30 | Internal review; Gal + Niranjan + Tomer sign-off | All |
| May 1 | **Submit to NeurIPS D&B track** | Samyak |

Seven-day buffer between experiment completion and submission.

## 9. Decisions needed from Gal

1. ☐ **GPT-5 tier** — standard ($1.25/$10) or Pro ($15/$120)? Recommend **standard**; Pro is ~12× more expensive.
2. ☐ **Azure quota** — Le, please confirm TPM/RPM on the GPT-5 thinking deployment. We need ≥200k TPM sustained to run without throttling concerns.
3. ☐ **Approve Option D** (main = pass@3 L0, ablation = pass@1 L1–L4, full kernel coverage). Total ~$843 on GPT-5 standard.
4. ☐ **Purge `gpt-4.1-mini`** from ParBench scripts, memory, and agenda (raw result JSONs stay on disk for audit)?
5. ☐ **Machines committed** — confirm Samyak's machine + Le's machine are both available for 2-day exclusive use between Apr 19–21.

---

## Appendix A — Statistical methodology details

**Pass@k estimator:** `scripts/analysis/statistical_analysis.py:706` implements the unbiased Chen et al. 2021 form:

$$ \text{pass@}k = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}} $$

where n = num_samples (3 for canonical, 1 for ablation), c = count of PASS results, k = query parameter.

**Per-cell delta confidence intervals:** For each (kernel, direction, model, L_k) cell, we have a binary outcome (PASS/FAIL) at L0 and at L_k. The paired comparison across cells can be reported as:
- Fraction of cells where L0 passes but L_k fails (regression rate)
- Fraction of cells where L_k passes but L0 fails (coincidence — should be small)
- 95% CI on Δpass@1 via paired bootstrap over (kernel, direction) cells

**Seed variance on canonical:** Each canonical cell has 3 independent samples. Report per-model standard deviation of pass@1 across the 3 samples in the paper's reproducibility section, addressing a well-known NeurIPS reviewer concern ([HumanEvalFix reproducibility study](https://www.mdpi.com/2674-113X/4/3/17)).

## Appendix B — Files referencing `gpt-4.1-mini` (removal scope)

```
scripts/analysis/selfrepair_analysis.py
scripts/analysis/test_cross_model_comparison.py
scripts/analysis/token_analysis.py
scripts/evaluation/analyze_eval.py
scripts/evaluation/llm_evaluate.py
scripts/evaluation/run_eval_batch.py
scripts/evaluation/test_generate_paper_figures.py
scripts/generate_paper_figures.py
scripts/batch/archive/rerun_conjunction_eval.sh
le_code/example_query.py
```

(Excludes `env_parbench/` vendored packages and stdlib references in `tiktoken`/`openai` which are not ParBench-owned.)

## Appendix C — Assumptions that could move the numbers

| Assumption | Sensitivity |
|---|---|
| Thinking avg 20k completion tokens/sample | If medium reasoning averages 10k → GPT-5 cost halves (~$376); if heavy 40k → doubles (~$1,504) |
| Together AI pricing ~$1 in / $2 out | Some listings quote $0.22/$1 → Qwen total < $50 (rounding noise at this scale) |
| 10-way task concurrency per machine | RTX 4070 GPU contention during CUDA builds may reduce to 5–8-way → wall-clock ~1.5×, still fits deadline |
| Azure TPM ≥ 200k on reasoning deployment | At 25k tokens/sample × 7,308 samples ≈ 183M tokens total; at 200k TPM would take ~15 hours if rate-limit-bound |

## Appendix D — Sources

- [Azure OpenAI pricing (official)](https://azure.microsoft.com/en-us/pricing/details/azure-openai/)
- [GPT-5 API pricing](https://pricepertoken.com/pricing-page/model/openai-gpt-5)
- [Together AI pricing page](https://www.together.ai/pricing)
- [Azure OpenAI quotas + limits](https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits)
- [ParEval benchmark (Nichols et al., HPDC 2024)](https://arxiv.org/abs/2401.12554)
- [HPC-Coder-v2](https://arxiv.org/abs/2412.15178)
- [Chen et al. 2021 pass@k estimator (Codex paper)](https://arxiv.org/abs/2107.03374)
- [HumanEvalFix reproducibility study](https://www.mdpi.com/2674-113X/4/3/17)
- [CrystalBLEU code-similarity metric (Eghbali et al., ASE 2022)](https://software-lab.org/publications/ase2022_CrystalBLEU.pdf)
