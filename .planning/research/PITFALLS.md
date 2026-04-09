# Domain Pitfalls: ParBench Pipeline Audit & Multi-Model Evaluation

**Domain:** LLM benchmark evaluation pipeline for HPC parallel code translation  
**Researched:** 2026-04-09  
**Scope:** Audit hardening, multi-suite coverage, multi-model comparison, TDD, statistical reporting  
**Confidence:** HIGH — grounded in actual codebase analysis plus verified external literature

---

## Critical Pitfalls

Mistakes that cause wrong results in the paper or require full reruns.

---

### Pitfall 1: Rodinia-Only EXCLUDED_SPECS Hardcodes Miss Future HeCBench/XSBench KNOWN_FAIL Specs

**What goes wrong:** `EXCLUDED_SPECS` in both `analyze_eval.py` and `generate_paper_data.py`
is a hardcoded frozenset of six Rodinia-prefixed spec IDs. When HeCBench Campaign 1 or
Campaign 2 results land on disk (hecbench-stencil1d-omp_target, hecbench-scan-omp_target
are already KNOWN_FAIL), the exclusion lists in these two files will be out of sync — those
results will be silently counted in the denominator, inflating the pass rate or distorting
the failure taxonomy.

**Why it happens:** The exclusion list was authored when only Rodinia specs existed. The
two files maintain parallel copies (copy-paste, not shared import), so updating one does not
update the other.

**Consequences:** A KNOWN_FAIL HeCBench target (e.g., stencil1d-omp_target) appearing in
the denominator makes the per-suite HeCBench pass rate look worse than it is; the paper
claim "31.0% non-KNOWN_FAIL pass rate" becomes wrong for multi-model comparison runs that
include HeCBench.

**Warning signs:**
- `file_counts.excluded_known_fail` in paper_data.json does not match `len(EXCLUDED_SPECS)`
  in the file that generated it.
- HeCBench KNOWN_FAIL spec IDs appear in per-kernel failure breakdown tables.
- The two `EXCLUDED_SPECS` frozensets diverge when grep'd across the repo.

**Prevention:**
- Centralize EXCLUDED_SPECS as a single authoritative source (e.g., a function in a shared
  `harness/known_fail.py` or loaded from `known-issues.md` at runtime). Both analysis
  scripts import from it.
- Add an assertion test: `assert EXCLUDED_SPECS == load_from_canonical_source()`.
- When adding any new KNOWN_FAIL spec to known-issues.md, the TDD test suite must fail until
  the exclusion is propagated everywhere.

**Phase:** Addresses Milestone 2 / harness + eval pipeline audit stage.

---

### Pitfall 2: _kernel_from_spec Parses Suite-Prefixed IDs Incorrectly for Multi-Part Kernel Names

**What goes wrong:** `_kernel_from_spec("rodinia-bfs-cuda")` returns `"bfs"` (correct).
`_kernel_from_spec("hecbench-stencil1d-omp_target")` returns `"stencil1d"` (correct).
But `_kernel_from_spec("rodinia-hotspot3d-cuda")` returns `"hotspot3d"` (correct).
The fragile case: HeCBench kernels with hyphenated names like `hecbench-scan-omp_target`
— the function uses `"-".join(parts[1:-1])` which gives `"scan"` here (OK), but a kernel
named `"fft-r2c"` would produce `"fft-r2c"` from `hecbench-fft-r2c-cuda`, which may or
may not be intended. This creates inconsistency between `by_kernel` groupings and
`by_direction` breakdowns when directions are inferred from `_direction_from_ids`.

**Why it happens:** The function was written when only Rodinia specs existed; all Rodinia
kernel names are single-word. The function is duplicated in `analyze_eval.py` and
`generate_paper_data.py` without shared tests.

**Consequences:** Cross-model comparison (`cross_model_comparison.py`) uses `by_kernel`
keys to compute `common_kernels` intersection. If kernel name extraction differs between
script runs or across suites, kernels silently fall out of the intersection, reducing the
valid comparison set without any warning.

**Warning signs:**
- `common_kernels` in cross_model_comparison.json has unexpectedly fewer entries than
  `by_kernel` for either model.
- `both_fail` + `both_pass` + `qwen_only_pass` + `gpt_only_pass` does not equal the count
  of kernels that appear in both models' data.

**Prevention:** Write a parametrized pytest covering all five suite prefixes and hyphenated
kernel names. Verify canonical kernel name extraction is identical in all scripts that use it.

**Phase:** Milestone 2, TDD coverage for results analysis.

---

### Pitfall 3: Suite-Asymmetric Denominator in Cross-Model Comparison

**What goes wrong:** Qwen Campaign 1 covered all 5 suites. GPT-4.1 mini results (897 files,
209 non-Rodinia invalid) effectively covered mainly Rodinia. `cross_model_comparison.py`
computes the intersection of directions and kernels, but does not enforce that both models
have results for the same set of benchmark suites. If the intersection collapses to
Rodinia-only, the comparison is valid only for Rodinia, but the paper may not say that.

**Why it happens:** The comparison script computes the intersection at the direction/kernel
level, which is correct mechanically. The problem is that no assertion or warning is emitted
when the intersection is dramatically smaller than one model's full coverage. A reader who
doesn't inspect the `missing` field in the output JSON will not notice.

**Consequences:** Claiming "Model A outperforms Model B across all translation directions"
when the comparison only covers Rodinia (60 of 96 specs) is misleading. HeCBench kernels
(10 kernels, different algorithmic character) are silently excluded.

**Warning signs:**
- `common_dirs` in cross_model_comparison.json lists only `cuda-to-omp`, `omp-to-cuda`, etc.
  with no HeCBench-sourced directions.
- `missing` section of the comparison JSON is non-empty and lists an entire suite's directions.
- Total records for model B in comparison << total records for model A.

**Prevention:**
- The comparison script must emit a structured warning when the two models' suite coverage
  differs by more than one suite. Require callers to acknowledge the asymmetry explicitly.
- Paper text must state which suites are included in each comparison and why.
- Run a dedicated multi-suite coverage check as a TDD fixture.

**Phase:** Milestone 2, results analysis audit; Milestone 3, paper methodology section.

---

### Pitfall 4: False Positive via Exit-Code-Only Verification (Already Happened Once, Can Recur)

**What goes wrong:** The verifier returns PASS if the binary exits with code 0 and the spec
lacks a `stdout_pattern` strategy. This already caused 9 FALSE_PASS specs (S-VERIFY bug,
fixed 2026-03-27). Newly added specs — from HeCBench expansion or AskSage Campaign runs —
are at high risk of starting with exit_code-only verification if the spec author does not run
the reference binary and capture its stdout.

**Why it happens:** Writing a spec is faster without running the binary. Exit code 0 is
visually reassuring. The distinction between "compiled and ran without crashing" and
"produced correct output" is easy to conflate when authoring specs in bulk.

**Consequences:** LLM translations that compile and run but produce wrong output (wrong
checksums, zero output, garbage output) will be counted as PASS. This inflates pass rate
and makes the benchmark useless as a correctness measure.

**Warning signs:**
- New spec has `verification.strategies` containing only `{"type": "exit_code", ...}`.
- `overall_status: PASS` on a result where `run_stdout_snippet` is empty or contains only
  timing output.
- A translated binary that outputs a different numeric checksum from the reference baseline
  still passes.

**Prevention:**
- TDD gate: a pytest fixture that reads every spec file and asserts `stdout_pattern` is
  present unless the spec has an explicit `"stdout_pattern_exempt": true` flag with a
  documented reason.
- Spec authoring protocol: run the reference binary, capture stdout, write the pattern
  from actual output, commit alongside the spec. This is already the documented process
  but is not mechanically enforced.
- For HeCBench specs added in the audit: do not add any spec to the eval batch until its
  `stdout_pattern` has been verified against the reference binary output.

**Phase:** Milestone 2, spec audit stage (benchmark sources).

---

### Pitfall 5: AskSage Non-OpenAI Response Format Causes Silent Extraction Failure

**What goes wrong:** AskSage's `/server/query` endpoint returns JSON in a non-OpenAI
format: the response content is under a `response` key (not `choices[0].message.content`),
and authentication uses `x-access-tokens` header with a token that expires every 24 hours
(must be refreshed via `/get-token-with-api-key`). If the adapter treats AskSage responses
as OpenAI-compatible, `call_llm()` will raise a `KeyError` or `AttributeError` on the
response, the retry loop will exhaust all attempts, and every task will be written as
`overall_status: ERROR` with an opaque error message — appearing superficially as
"API failures" rather than an adapter bug.

**Why it happens:** The current `call_llm()` dispatches on model name prefix. AskSage
models will need a new dispatch branch. The 24-hour token expiry means a batch run
that starts at 22:00 will have an expired token before it finishes at 02:00 the next day.

**Consequences:** An entire Campaign 2 batch run produces 0 PASS, 0 BUILD_FAIL, N ERROR —
misinterpreted as "models hosted on AskSage cannot translate code," corrupting the paper's
multi-model comparison.

**Warning signs:**
- All results for an AskSage-routed model have `overall_status: ERROR`.
- `error_message` contains `KeyError: 'choices'` or `AttributeError: 'str' object has no
  attribute 'choices'`.
- Batch run spans midnight; errors begin at approximately the 24-hour mark after token
  generation.

**Prevention:**
- Write the AskSage adapter with an explicit response schema test before running any real
  eval. Mock the endpoint in unit tests with the actual observed JSON structure.
- Implement token refresh as a first-class concern: check token expiry before each call
  and refresh proactively when less than 30 minutes remain.
- Add a `--dry-run` path for AskSage that hits the endpoint with a minimal prompt and
  validates the response structure without writing any result files.
- Confirm the full response schema with the Argonne researcher before writing any adapter
  code. "Response format awaiting researcher confirmation" (PROJECT.md) must be resolved
  before the adapter ships.

**Phase:** Milestone 2, AskSage adapter task.

---

### Pitfall 6: pass@k Denominator Mismatch Between Campaign 1 and Campaign 2

**What goes wrong:** Campaign 1 uses `temp=0.0` (deterministic, self-repair up to 3
retries, L0-L4). Campaign 2 uses `temp=0.7` (stochastic, single-shot, L0 only, k=3
samples). `generate_paper_data.py` splits records by `temperature` field. A result file
written without a `temperature` field (e.g., legacy files or files from an adapter that
omits it) defaults to `0.0` and is assigned to Campaign 1, inflating Campaign 1's
denominator with what may be stochastic samples.

**Why it happens:** The temperature field is written by `llm_evaluate.py` now, but older
result files (the 1,248 existing Qwen files) have the field populated. The AskSage adapter
may omit it if not explicitly threaded through.

**Consequences:** Wilson CI bounds for Campaign 1 and pass@k estimates for Campaign 2
will be wrong if even a few records are in the wrong bucket. McNemar test for
direction asymmetry relies on paired Campaign 1 data — contamination breaks pairing.

**Warning signs:**
- `file_counts.primary_campaign + file_counts.passk_campaign != file_counts.total_on_disk`
  (minus excluded KNOWN_FAIL count).
- Campaign 2 sample size at a given task is not exactly k (e.g., 1 or 2 instead of 3).
- A `temperature` field is absent from result JSON files produced by a new adapter.

**Prevention:**
- Assert in the adapter that every result JSON written includes `"temperature"` as an
  explicit field (not inferred from filename).
- Add a TDD fixture: load all existing result JSONs and assert `"temperature" in result`.
- For pass@k estimation, assert that every task in Campaign 2 has exactly k samples before
  computing the unbiased estimator.

**Phase:** Milestone 2, eval pipeline audit; Campaign 2 implementation.

---

## Moderate Pitfalls

---

### Pitfall 7: Thinking Mode Asymmetry Across Models

**What goes wrong:** Qwen 3.5 397B has thinking enabled by default (Together AI endpoint
requires explicit `enable_thinking: False` via `chat_template_kwargs`). Gemini 2.5 Flash
requires `reasoning_effort="none"`. Claude models do not have a thinking toggle at the base
API level. OpenAI o3/o4 reasoning models do not accept `temperature` at all. If the AskSage
adapter does not control thinking for models that support it, some models will use extended
inference-time reasoning while others will not, making the comparison invalid.

**Why it happens:** This was already discovered and fixed for existing adapters (confirmed by
Gemini investigation 2026-03-26). AskSage exposes many models under one endpoint; it is
unclear whether model-level thinking controls are accessible or respected via the API.

**Consequences:** A model that uses chain-of-thought reasoning at inference time will appear
to outperform an equivalent model without it. The performance gap attributed to "model
quality" is actually "reasoning mode used."

**Warning signs:**
- Completion token counts for one model are 5-10x higher than another model on the same
  task (thinking tokens are included in completion tokens by most providers).
- `finish_reason: "max_tokens"` is far more common for one model than others.

**Prevention:**
- Document the thinking/reasoning mode for every model in the results JSON (`"thinking_disabled": true/false`).
- For AskSage-hosted models, confirm with the researcher whether thinking mode is
  controllable and if so, enforce it off for all eval models.
- Reject comparison results where thinking mode differs between models being compared.

**Phase:** Milestone 2, AskSage adapter; Milestone 3, paper methodology.

---

### Pitfall 8: Suite-Level Analysis Scripts Not Updated for Non-Rodinia Suites

**What goes wrong:** Several analysis scripts are named with explicit suite references:
`analyze_rodinia_batch.py`, `analyze_cuda_batch.py`, `analyze_omp_batch.py`. These are
likely hardcoded to specific directory paths, model names, or spec prefixes. When
multi-suite Campaign 1 results arrive (HeCBench, XSBench, RSBench, mixbench), these scripts
will either silently ignore non-Rodinia data or crash on unexpected spec ID formats.

The more insidious case: `generate_paper_data.py` has a `--suite` flag that filters only
the PRIMARY campaign but explicitly does NOT filter the pass@k campaign ("intentionally NOT
filtered"). If a caller mistakenly passes `--suite rodinia` when generating multi-model
paper data, the primary campaign numbers reflect Rodinia only, but the pass@k numbers
reflect all suites — producing internally inconsistent statistics.

**Why it happens:** The suite filter asymmetry was an intentional design decision for a
previous sprint (SC26). For NeurIPS, with 5 suites and multi-model comparison, this
asymmetry is a correctness hazard.

**Prevention:**
- Audit `analyze_rodinia_batch.py`, `analyze_cuda_batch.py`, `analyze_omp_batch.py` for
  hardcoded Rodinia paths and update or deprecate them.
- Add a warning to `generate_paper_data.py` that fires when `--suite` is set and pass@k
  records span multiple suites.
- Write a TDD test that runs `generate_paper_data.py` with all 5 suites present and checks
  that `suite_filter: null` produces consistent primary and pass@k denominators.

**Phase:** Milestone 2, results analysis audit.

---

### Pitfall 9: Cross-API Verification Uses Source Run Args for Non-Kernel-Only Targets

**What goes wrong:** `_build_cross_api_run_spec()` sends source run args to the translated
binary for non-kernel-only (full-program) translations (CUDA↔OMP). This was the correct fix
for the S-OCLFIX bug (2026-03-30) — OpenCL translations are kernel-only and must use target
args. But if a future translation direction is partially kernel-only (e.g., a hybrid where
both host and kernel are translated), the `_is_kernel_only_translation()` predicate based on
`.cl` file extension will misclassify it.

**Why it happens:** The current heuristic (`all(fname.endswith(".cl") for fname in targets)`)
is correct for existing specs but is a property of file extension, not an explicit spec-level
declaration of translation semantics.

**Prevention:**
- Add a `"translation_type": "kernel_only" | "full_program"` field to spec JSON for all 96
  specs. Use the extension heuristic only as a fallback with a warning.
- TDD: assert that every spec in the manifest that has `.cl` in `translation_targets` also
  has `translation_type: "kernel_only"` in the spec file (or document why not).

**Phase:** Milestone 2, harness pipeline audit.

---

### Pitfall 10: Augmentation Level-Invariance Claim Rests on Rodinia Baseline Only

**What goes wrong:** The key claim "augmentation introduces zero new failures — results are
level-invariant" (PASS at L1 implies PASS at L4) was verified for 54/60 Rodinia specs and
4 XSBench specs (2026-03-20). HeCBench, RSBench, and mixbench specs were NOT part of that
verification. With 10 HeCBench kernels and more complex multi-file structures, it is not
guaranteed that the 6 AST transforms are semantics-preserving on HeCBench code.

**Why it happens:** The augmentation baseline was established before HeCBench specs were
finalized. The claim was promoted to the paper without noting the scope limitation.

**Consequences:** If level-invariance does not hold for HeCBench at L2-L4, the paper's
augmentation robustness claim is overstated. Worse, eval results at L2-L4 for HeCBench will
appear to show "degradation under augmentation" that is actually a spec/transform bug.

**Warning signs:**
- Augmentation retest at L1-L4 for HeCBench shows a different PASS count at L3 vs L1.
- A specific HeCBench kernel fails at L2 but passes at L0 and L1.
- `ChangeFunctionNames` or `PointerArithmeticToArrayIndex` fires on a HeCBench kernel with
  complex host-device boundary code and breaks compilation.

**Prevention:**
- Before running Campaign 1 at L1-L4 for HeCBench, run the augmentation harness retest
  on all 23 passing HeCBench specs at L1-L4 (same protocol as the Rodinia M10b retest).
- Add a TDD fixture that runs augmentation at all levels on a representative HeCBench spec
  and asserts PASS.

**Phase:** Milestone 2, benchmark sources audit.

---

### Pitfall 11: TDD Mocking at the Wrong Layer Creates Tests That Do Not Catch Real Bugs

**What goes wrong:** When writing TDD for the eval pipeline, the temptation is to mock
`call_llm()` entirely and return a canned translated file. This confirms that the extraction,
build, run, and verify stages work — but does not test that the prompt was constructed
correctly or that the LLM response parsing handles edge cases (missing code fences, extra
text, partial extraction).

Conversely, mocking at the HTTP level (intercepting `requests.post` or `openai.Client`) is
too low-level: it couples tests to the internal implementation of the SDK, making them
brittle to SDK version upgrades.

**Why it happens:** LLM API calls are expensive and non-deterministic. The natural reflex is
to mock them entirely. But "mock at `call_llm()`" means the extraction logic, retry loop,
and response normalization are never tested.

**Consequences:** A real bug in file extraction regex (as happened with the inline `(?i)`
regex combiner) would not be caught by mocked tests that return pre-extracted file dicts.
The pipeline passes all tests but fails on real LLM output.

**Prevention:**
- Mock at the `call_llm()` boundary (not below it), but supply realistic fixture responses
  that include: correct code fences, malformed code fences, truncated responses (finish_reason
  "length"), partial extraction (only one of two required files present).
- Maintain a corpus of real LLM responses (anonymized, stored as fixture JSON) that cover
  known edge cases. Tests that parse these responses are the highest-value regression tests.
- Never mock the extraction logic, retry orchestration, or verification stage — these must
  be integration-tested with realistic inputs.
- For the AskSage adapter specifically: write a separate unit test for response parsing that
  uses the actual observed JSON structure (not OpenAI format).

**Phase:** Milestone 2, TDD coverage task.

---

## Minor Pitfalls

---

### Pitfall 12: Wilson CI Widths Are Misleading at Per-Kernel Granularity with Small n

**What goes wrong:** Wilson CIs are computed for every `by_kernel` and `by_direction`
slice in `generate_paper_data.py`. A kernel with n=8 results (e.g., 8 direction × level
combinations) has a CI width of approximately ±30% at 95% confidence — too wide to draw
any directional conclusion. The `sample_size_flags` section exists to catch this, but the
thresholds (`MIN_L0_SAMPLE_SIZE: 10`, `MIN_PASSK_TASK_SAMPLES: 3`) may not be propagated
into the paper text.

**Warning signs:**
- A per-kernel CI in the paper spans 0.10 to 0.75.
- A claim like "kernel X is harder than kernel Y" based on point estimates without reporting
  the CI widths or n values.

**Prevention:**
- Paper tables must report n alongside pass rate and CI.
- Any directional claim ("X > Y") must be accompanied by a statistical test
  (chi-squared or Fisher's exact), not just CI overlap inspection.
- Use `SAMPLE_SIZE_ADEQUACY_THRESHOLD: 10` as the hard floor; do not report per-kernel
  conclusions for kernels below this threshold.

**Phase:** Milestone 3, paper results section.

---

### Pitfall 13: Goodhart's Law on pass@1 as Primary Metric

**What goes wrong:** The paper uses pass@1 (Campaign 1) as the primary correctness metric.
This measures the probability a single deterministic sample passes. But because
`temp=0.0` makes the output fully deterministic, pass@1 here means "this specific prompt
produces a passing translation." A model with high pass@1 that happens to have seen
Rodinia-like code heavily in training may not generalize. This is not a methodological
flaw but must be acknowledged: pass@1 at temp=0 is a single point on the capability curve,
not an unbiased estimate of model quality.

**Warning signs:**
- The paper makes claims about "general parallel code translation ability" based solely on
  Rodinia pass@1 numbers.
- No diversity metric (e.g., diversity of failure modes, per-suite breakdown) accompanies
  the aggregate pass@1 claim.

**Prevention:**
- Campaign 2 (pass@k at temp=0.7) exists precisely to provide a stochastic capability
  estimate. Always report both campaigns for NeurIPS.
- Report per-suite pass rates: Rodinia, HeCBench, XSBench, RSBench, mixbench separately.
  If Rodinia dominates the aggregate, say so explicitly.

**Phase:** Milestone 3, paper framing.

---

### Pitfall 14: File Timestamp Collisions Cause --resume to Skip Rerun Tasks

**What goes wrong:** `run_eval_batch.py` uses `--resume` to skip tasks where a result
file already exists. If two concurrent eval sessions write result files with the same name
(e.g., `qwen_hecbench` and `qwen_small` tmux sessions both run overlapping spec lists),
one session's result may be overwritten mid-write, producing a truncated or corrupt JSON.
On the next `--resume` run, the corrupt file is detected but silently skipped or raises a
non-fatal `json.JSONDecodeError` (caught in `load_results()`), leaving a permanent gap in
coverage.

**Warning signs:**
- A spec that was supposedly in the eval batch has no corresponding result file despite
  `--resume` completing without error.
- `json.JSONDecodeError` appears in eval batch logs alongside a specific result filename.
- `file_counts.total_on_disk` is less than expected given the batch size.

**Prevention:**
- Ensure tmux sessions cover disjoint spec/direction sets. Verify with grep before starting
  any new batch.
- Write result files atomically (write to a `.tmp` file, then rename) to prevent corrupt
  JSON from partial writes.

**Phase:** Milestone 2, eval pipeline audit.

---

### Pitfall 15: Tokenization and Max-Tokens Ceiling Differ Across Provider APIs

**What goes wrong:** Anthropic, Together AI, and AskSage have different maximum completion
token limits and different tokenizers. `llm_evaluate.py` sets `max_tokens=32768` for
Anthropic, `max_tokens=81920` for Qwen/Together, and `max_tokens=65536` for Gemini.
For AskSage-hosted models, the ceiling is unknown until confirmed. If an AskSage model has
a lower ceiling than 32768, multi-file kernels (myocyte: 10 target files, heartwall: 3 files)
will be truncated, producing partial code that builds but is wrong — or simply fails with
`finish_reason: "length"`.

This already caused data loss for groq-llama-3.3-70b (16384 token cap, myocyte and heartwall
affected). The same class of bug will recur for any new model whose token ceiling is not
verified before running multi-file kernels.

**Warning signs:**
- `finish_reason: "length"` in result JSON for any multi-file kernel.
- EXTRACTION_FAIL or BUILD_FAIL on multi-file kernels only (not single-file kernels).
- Completion token count equals exactly the configured `max_tokens` limit.

**Prevention:**
- Before running any new model through the eval pipeline, send a synthetic long-output
  prompt to verify the effective completion token ceiling.
- Maintain a per-model token ceiling registry in `llm_evaluate.py` (extend `MODEL_REGISTRY`
  with a `max_completion_tokens` field).
- For models where the ceiling is below 65536, skip multi-file kernels explicitly with a
  logged warning, rather than running them and getting EXTRACTION_FAIL.

**Phase:** Milestone 2, AskSage adapter; multi-model Campaign runs.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Spec audit (all 5 suites) | Exit-code-only specs (Pitfall 4) | TDD gate: assert stdout_pattern present |
| HeCBench augmentation baseline | Level-invariance not verified (Pitfall 10) | Run M10b-protocol retest before L1-L4 evals |
| AskSage adapter implementation | Silent ALL-ERROR batch (Pitfall 5) | Dry-run + schema test before real eval |
| AskSage adapter implementation | Token ceiling unknown (Pitfall 15) | Verify ceiling before multi-file kernels |
| AskSage adapter implementation | Thinking mode uncontrolled (Pitfall 7) | Confirm with researcher, enforce off |
| Campaign 2 pass@k | Temperature field missing (Pitfall 6) | Assert field present in every result JSON |
| Results analysis | EXCLUDED_SPECS stale (Pitfall 1) | Centralize, add assertion test |
| Cross-model comparison | Suite asymmetric denominator (Pitfall 3) | Emit structured warning when coverage differs |
| Cross-model comparison | Kernel name extraction inconsistency (Pitfall 2) | Parametrized pytest for all suite prefixes |
| TDD harness tests | Mocking at wrong layer (Pitfall 11) | Mock at call_llm boundary only, use real fixtures |
| Paper writing | Wilson CI too wide at per-kernel (Pitfall 12) | Report n, use chi-squared not CI overlap |
| Paper writing | pass@1 overstated (Pitfall 13) | Report both campaigns, per-suite breakdown |
| Concurrent eval sessions | File collision (Pitfall 14) | Verify disjoint spec sets, atomic file writes |
| Non-kernel-only spec authoring | Cross-API run arg mismatch (Pitfall 9) | Add explicit translation_type field to specs |

---

## Sources

- Codebase analysis: `scripts/evaluation/analyze_eval.py`, `scripts/analysis/generate_paper_data.py`,
  `scripts/analysis/cross_model_comparison.py`, `scripts/evaluation/llm_evaluate.py`,
  `harness/verifier.py` — direct inspection, HIGH confidence
- `.claude/rules/known-issues.md` and `known-issues-archive.md` — project incident history,
  HIGH confidence (first-hand)
- `.planning/PROJECT.md` — current sprint constraints, HIGH confidence
- Chen et al. 2021 "Evaluating Large Language Models Trained on Code" (HumanEval paper) —
  pass@k unbiased estimator; statistical pitfalls with small n — MEDIUM confidence
  (well-established but training-data vintage)
- MLOps Community / DAGWorks: mocking LLM APIs in TDD pipelines — MEDIUM confidence (verified
  pattern matches codebase structure)
- AskSage documentation (`docs.asksage.ai`) and GitHub community repo — non-OpenAI API format,
  24-hour token expiry, `/server/query` endpoint — MEDIUM confidence (doc confirmed, response
  schema not yet confirmed by Argonne researcher)
- ALCF inference endpoints (`docs.alcf.anl.gov`) — OpenAI-compatible alternative to AskSage
  at same institution — LOW confidence (parallel system, may or may not be the one used)
