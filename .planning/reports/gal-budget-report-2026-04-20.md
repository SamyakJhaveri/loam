# Phase 3 Budget — GPT-5.4

**Phase 3 GPT-5.4 estimated at $94 (Standard sync) or $47 (Batch API) at the mid L0-pass scenario.**

Phase 3 scope: all 6 directions (cuda↔omp, cuda↔opencl, omp↔opencl) × canonical pass@3 at L0 + L0-conditional ablation pass@1 at L1–L4; temperature 0.7; reasoning effort `medium`. GPT-5.4 only.

## Bottom line — total Phase 3 cost

Rows: model × API mode. Columns: L0 ablation-conditioning rate. Mid is the planning value.

| Model / Mode | Low (30% L0) 1,117 samples | **Mid (50% L0) 1,330 samples** | High (75% L0) 1,596 samples |
|---|---|---|---|
| gpt-5.4 Standard | $79.08 | **$94.16** | $113.00 |
| gpt-5.4 Batch | $39.54 | **$47.08** | $56.50 |
| gpt-5.1 Standard | $56.74 | **$67.56** | $81.08 |
| gpt-5.1 Batch | $28.26 | **$33.65** | $40.38 |

### At-a-glance (mid 50% L0, 1,330 samples)

```
gpt-5.4 Standard  ██████████████████████████████████████████████  $94.16
gpt-5.4 Batch     ███████████████████████                         $47.08
gpt-5.1 Standard  █████████████████████████████████               $67.56
gpt-5.1 Batch     ████████████████                                $33.65
                  └─────────────┬─────────────┬──────────────┐
                  $0           $25           $50          ~$100
```

Batch halves the cost at a 24-hour SLA. gpt-5.1 is ~28% cheaper than gpt-5.4 per token at both tiers.

## Per-sample cost

Computed from mean smoke-v4 tokens (2,450 input + 4,312 output). Output tokens include reasoning tokens — Azure bundles `reasoning_tokens` into `completion_tokens_details`, which bills as completion.¹

| Model / Mode | Input $/sample | Output $/sample | Total $/sample |
|---|---|---|---|
| gpt-5.4 Standard | $0.00613 | $0.06468 | $0.0708 |
| gpt-5.4 Batch | $0.00306 | $0.03234 | $0.0354 |
| gpt-5.1 Standard | $0.00338 | $0.04743 | $0.0508 |
| gpt-5.1 Batch² | $0.00153 | $0.02372 | $0.0253 |

## Sample count breakdown

Manifest-eligible cells per direction (authoritative, from `manifest.jsonl` 2026-04-20):

| Direction | Cells | Canonical (×3) | Ablation L1–L4 (mid, ×0.5×4) |
|---|---|---|---|
| cuda-to-omp | 84 | 252 | 168 |
| omp-to-cuda | 84 | 252 | 168 |
| cuda-to-opencl | 25 | 75 | 50 |
| opencl-to-cuda | 25 | 75 | 50 |
| omp-to-opencl | 24 | 72 | 48 |
| opencl-to-omp | 24 | 72 | 48 |
| **Total** | **266** | **798** | **532 (mid)** |

Phase 3 totals by L0 scenario: **1,117 (low) / 1,330 (mid) / 1,596 (high)**.

## Token basis

Smoke v4 measured, 8 unique azure-gpt-5.4 samples, post-retry-collapsed.³

| Metric | Value |
|---|---|
| Mean prompt_tokens | 2,450 |
| Mean completion_tokens | 4,312 |
| p95 completion_tokens | 5,797 |
| Reasoning effort | medium |

## Model trade-off

- **gpt-5.4** is the current flagship; strongest reasoning and calibration. Used for all smoke-v4 measurements. No capability risk.
- **gpt-5.1** is ~28% cheaper on input and ~27% cheaper on output per token. Reasoning quality measurably below 5.4 on translation/repair tasks in public benches; no ParBench-specific evidence either way.
- **Batch API** (both models) halves the per-token rate at a 24h SLA. No capability loss; completions are identical. Compatible with Phase 3 scheduling (Phase 3 is not latency-bound).

## Azure Batch API — feasibility for Phase 3

Batch API is the 50%-discount path. Two conditions must hold before we can quote it as real.

### Availability (Azure Foundry public docs, updated 2026-04-14)

| Model | Global Batch tier listed? |
|---|---|
| gpt-5.1 | Yes (all major regions) |
| gpt-5.4 | **Not listed** — batch rollout may not yet include 5.4. Requires direct verification in the Foundry portal. |

If gpt-5.4 is not yet on Batch, the gpt-5.4 Batch column in the cost table is aspirational, not committed.

### Pipeline architecture compatibility

ParBench's current eval pipeline calls `client_az.chat.completions.create()` synchronously at `scripts/evaluation/llm_evaluate.py:951` and immediately consumes the response (write files → build → run → verify → decide retry). Batch API is async: submit JSONL → wait ≤24 h → retrieve result JSONL.

| Phase 3 config | Batch-compatible? |
|---|---|
| Canonical pass@3 at L0 with `--max-retries 1` (zero-shot) | **Yes** — via adapter layer. |
| Ablation pass@1 at L1–L4 with `--max-retries 1` (zero-shot) | **Yes** — via same adapter. |
| Iterative repair (`--max-retries > 1`) | **No** — repair prompt N+1 embeds attempt N's compiler stderr. Architecturally incompatible. Not in Phase 3 scope. |

Since Phase 3 runs zero-shot (no iterative repair), batch adoption is feasible.

### Engineering cost to enable Batch

| Item | Shape |
|---|---|
| New `scripts/evaluation/azure_batch_adapter.py` | Submit JSONL, poll, retrieve, map responses to tasks via `custom_id`. ~150-200 LOC. |
| Refactor `evaluate_translation()` at `:1641` | Split into `build_prompt()` + `finish_from_llm_response()`. Latter invoked per retrieved response. |
| Tests | Grep-parity tests mirroring `tests/test_verifier_caller_contract.py` to lock the thinking-kwargs gate across sync + batch submission. |
| Estimated effort | 1-2 engineering days. |

### Constraints worth knowing

- Azure's "24h SLA" is aspirational. Jobs exceeding 24h keep running; no refund documented. Cost savings (~50%) is the only hard guarantee.
- `/v1/chat/completions` batch responses do **not** populate `reasoning_tokens`. If per-sample reasoning-token audit is needed for the paper, submit through `/v1/responses` instead (same model, different response shape).
- Reasoning models (GPT-5 family) reject `temperature`, `top_p`, `seed` on the underlying API — our pipeline already gates these at `llm_evaluate.py:940-950`. Batch submission inherits the same gate; no new risk.

## Recommendation

Two paths, ordered by expected cost:

1. **Preferred: gpt-5.4 via Batch API, ~$47 + 1-2 engineering days.** Verify gpt-5.4 Batch availability in the Foundry portal first. If available, invest the 1-2 days on the adapter; the 50% saving + the adapter's reusability across future model comparisons makes it net-positive.
2. **Fallback: gpt-5.4 via Standard sync, ~$94, zero engineering.** Run Phase 3 today without any code changes. Higher cost, but the engineering risk is zero and Phase 3 unblocks immediately.

If gpt-5.4 is confirmed not on Batch: **gpt-5.1 Standard at ~$68 is the next-best no-engineering option** (27% savings vs gpt-5.4 Standard, different model — accept a small capability trade-off). Pushing to gpt-5.1 Batch (~$34) requires the same adapter work as gpt-5.4 Batch.

## Appendix — calculation breakdown

Full derivation from first principles for audit.

### A. Token measurement (smoke v4, n=8)

Azure returns `prompt_tokens` (input) and `completion_tokens` (output) in each response JSON. `completion_tokens` already includes hidden `reasoning_tokens` (Azure bundles them for billing). Mean across 8 real GPT-5.4 calls:

- prompt_tokens mean: 2,450
- completion_tokens mean: 4,312

### B. Per-sample cost formula

$$\text{cost/sample} = \frac{\text{prompt tokens}}{10^6}\times\text{input \$/M} + \frac{\text{completion tokens}}{10^6}\times\text{output \$/M}$$

### C. Worked example (gpt-5.4 Standard)

- Input: $(2{,}450 / 10^6) \times \$2.50 = \$0.006125$
- Output: $(4{,}312 / 10^6) \times \$15.00 = \$0.06468$
- Total: **$0.0708/sample**

Batch tiers are exactly half because batch discount is 50% on both dimensions. Check: $0.0708 / 2 = $0.0354 ✓.

### D. Sample-count derivation

Manifest eligibility per direction (from `manifest.jsonl`):

- cuda↔omp: 84 kernels each direction = 168 cells
- cuda↔opencl: 25 each direction = 50 cells
- omp↔opencl: 24 each direction = 48 cells
- **Total: 266 cells across 6 directions**

Canonical: 266 cells × 3 samples (pass@3) = **798 samples**
Ablation: (cells passing L0) × 4 augmentation levels × 1 sample
- Low 30% L0: 80 × 4 = 319
- Mid 50% L0: 133 × 4 = 532
- High 75% L0: 200 × 4 = 798

### E. Total cost = samples × per-sample cost

Worked for gpt-5.4 Standard at mid scenario: 1,330 × $0.0708 = **$94.16** (matches headline).

### F. Delta from prior $848 estimate

The prior $848 figure used two inflated inputs: (i) assumed 5,000/20,000 input/output tokens per sample (smoke v4 measures 2,450/4,312), (ii) sample count built from 87 kernels × 6 directions = 522 cells (manifest-eligible actual: 266 cells). Each was ~2× inflated; combined effect roughly 4-10× depending on mode.

### G. Caveats affecting the numbers

1. n=8 tokens are from cuda↔omp pairs only; applied uniformly to opencl-direction samples. Reasonable (prompt structure is identical) but not measured.
2. L0 pass rate is unmeasured for gpt-5.4 on ParBench; mid 50% is a planning assumption.
3. gpt-5.1 Batch output rate is derived from the 50% rule; Azure does not publish it directly. Expect ±10% variation if billed differently.
4. `reasoning_tokens` are bundled into `completion_tokens` in current telemetry — we cannot separately audit reasoning-cost share.

---

¹ Azure Foundry Global public pricing, <272K context tier, verified 2026-04-19. gpt-5.4: $2.50/$15.00 per M (std) and $1.25/$7.50 per M (batch). gpt-5.1: $1.38/$11.00 per M (std) and $0.625/$5.50 per M (batch).
² gpt-5.1 batch output rate derived from the 50% batch-discount rule; Azure does not quote the output rate directly in the public schedule. Flag if billing returns a different number.
³ n=8 samples are cuda↔omp pairs. Token averages are used unchanged across all 6 directions.
