# Architecture Patterns: AskSage Adapter + Campaign 2

**Domain:** Non-OpenAI provider integration into an existing OpenAI-SDK-based multi-provider eval pipeline
**Researched:** 2026-04-09
**Confidence:** HIGH — based on direct code reading of the existing pipeline, not external sources

---

## Context: What Already Exists

The eval pipeline is built around a single function `call_llm()` in
`scripts/evaluation/llm_evaluate.py` (lines 730–1022). This function is a
**dispatch block** — a chain of `if/elif` branches keyed on model-name prefix.
Every branch returns an identical dict:

```python
{
    "response_text": str,
    "prompt_tokens": int,
    "completion_tokens": int,
    "finish_reason": str,   # normalized: "stop" | "length" | ...
    "duration_seconds": float,
}
```

All six existing providers (Anthropic, OpenAI, Azure, Groq, Gemini, Together AI) return
this exact shape. The rest of the pipeline — extraction, build, run, verify, result JSON
writing — never sees a provider object. It sees only this dict.

The file also contains a commented hint at line 764:
```python
# ParaCodex (future):
#     Add `elif model.startswith("paracodex")` branch here.
#     Same dict return format — rest of pipeline is unchanged.
```

This tells us the intended extension point: add an `elif model.startswith("asksage-")`
branch to `call_llm()`. AskSage is a new leaf in an existing dispatch tree, not a new
architectural layer.

---

## Recommended Architecture

### Pattern: Inline Branch in `call_llm()` (NOT a separate class or adapter module)

**Recommendation:** Add AskSage as an `elif` branch in `call_llm()`, following the
exact same pattern as the existing six providers. Do NOT introduce an abstract
`LLMProvider` class, a strategy interface, a separate `asksage_client.py` module, or
any protocol/ABC machinery.

**Why this is correct for this codebase:**

1. The existing dispatch is already the "strategy pattern" — each branch is a strategy,
   the `call_llm()` function is the context. The strategies are inlined because they are
   short (15–30 lines each) and share no state between calls.

2. The codebase has no other multi-provider abstraction to align with. Introducing a new
   abstraction layer here creates divergence from the existing six providers, making the
   code harder to audit (NeurIPS paper defensibility requires clean, auditable code).

3. The comment at line 764 is explicit design intent from the original author: "Add branch
   here. Same dict return format. Rest of pipeline is unchanged."

4. A separate `asksage_client.py` module adds a dependency boundary without a caller
   boundary — `call_llm()` would still be the only caller. The module boundary buys nothing.

**When to deviate from inline branch:** If AskSage requires >60 lines of HTTP logic (e.g.,
multi-step auth refresh, complex pagination, streaming response assembly), extract a
`_call_asksage()` private function in the same file and call it from the `elif` branch.
This keeps `call_llm()` scannable while isolating the complexity.

### Component Boundaries

```
scripts/evaluation/llm_evaluate.py
  └─ call_llm(model, system_msg, messages, ...)
       ├─ elif model.startswith("asksage-"):   ← NEW branch
       │    ├─ Read ASKSAGE_API_KEY from env
       │    ├─ POST https://api.asksage.anl.gov/server/query
       │    │    body: {token, message, model, ...}
       │    ├─ Parse response → extract response_text, token counts
       │    └─ Return normalized dict (same 5-key shape as all other providers)
       └─ (all existing branches unchanged)

MODEL_REGISTRY (top of llm_evaluate.py)
  └─ "asksage-{model_name}": {
         "provider": "asksage",
         "api_model": "{actual_model_id_for_POST_body}",
         "notes": "...",
     }
```

### Data Flow Through Provider Dispatch

```
run_eval_batch.py
  → evaluate_translation(source_path, target_path, model="asksage-llama3-70b", ...)
      → build_translation_prompt(...)             # unchanged
      → call_llm(model="asksage-llama3-70b", system_msg, messages, temperature)
          → AskSage POST /server/query
          ← raw JSON response (non-OpenAI format)
          → parse: extract text + token fields     # AskSage-specific, stays inside elif branch
          → return normalized 5-key dict           # identical shape to all other providers
      → extract_code_blocks(response_text, ...)    # unchanged
      → build/run/verify via harness               # unchanged
      → write result JSON                          # unchanged
```

The normalization boundary is the `return` statement inside the `elif` branch. Nothing
outside `call_llm()` is aware that AskSage exists.

---

## Handling Unknown/Partial Response Schema

**Problem:** AskSage response schema is TBD — endpoint and auth are confirmed, but the
exact JSON structure (field names for response text, token counts, finish reason) is
pending researcher confirmation.

**Recommended approach: Defensive extraction with explicit fallbacks.**

```python
# Inside the elif asksage- branch, after receiving response_json:

response_text = (
    response_json.get("response")        # try field "response"
    or response_json.get("message")      # fallback: "message"
    or response_json.get("content")      # fallback: "content"
    or response_json.get("text")         # fallback: "text"
    or ""
)

# Token counts: AskSage may not expose these — default to 0, log a warning
prompt_tokens = response_json.get("usage", {}).get("prompt_tokens", 0)
completion_tokens = response_json.get("usage", {}).get("completion_tokens", 0)
if prompt_tokens == 0:
    logger.warning(
        "AskSage did not return token counts for model=%s — "
        "prompt_tokens/completion_tokens will be 0 in result JSON. "
        "Update extraction once schema is confirmed.",
        model,
    )

finish_reason = response_json.get("finish_reason", "stop")
```

**Design principle:** Zero is a valid token count in the result JSON — the analysis scripts
handle null/zero token counts already (they compute ratios on non-zero values only). The
result JSON schema does not require token counts to be non-zero. This means AskSage results
are valid even before the schema is confirmed, as long as `response_text` is correctly
extracted.

**Schema discovery process:**
1. Write the branch with the defensive extraction above.
2. Run a single dry-run task: `python3 scripts/evaluation/llm_evaluate.py --dry-run ...`
   (this will not hit AskSage).
3. Run a single live task with `--verbose` and log the full raw response JSON before parsing.
4. Confirm field names with researcher, then harden the extraction.

**Log the full raw response on first use:**
```python
if verbose:
    logger.debug("AskSage raw response: %s", json.dumps(response_json, indent=2))
```
This makes field discovery cheap: run once with `-v`, grep the log for the actual keys.

**Do NOT write a "schema version" switch or a config-driven field mapping.** AskSage is one
provider with one schema. Complexity that would be justified for a plugin architecture is
unnecessary here.

---

## Rate Limits, Retries, and Provider Isolation

**Problem:** AskSage may have different rate limits, HTTP error formats, and retry
semantics than the OpenAI SDK providers. The existing pipeline has NO retry logic
inside `call_llm()` — all retries are the self-repair loop in `evaluate_translation()`,
which retries on BUILD_FAIL, not on API errors.

**Recommended approach: Narrow HTTP retry wrapper, local to the AskSage branch.**

```python
elif model.startswith("asksage-"):
    api_key = os.environ.get("ASKSAGE_API_KEY")
    ...
    MAX_HTTP_RETRIES = 3
    RETRY_DELAY_SECONDS = 10.0

    for attempt in range(MAX_HTTP_RETRIES):
        try:
            resp = requests.post(
                "https://api.asksage.anl.gov/server/query",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            response_json = resp.json()
            break
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else None
            if status_code == 429 and attempt < MAX_HTTP_RETRIES - 1:
                logger.warning("AskSage rate-limited (429), retrying in %ss", RETRY_DELAY_SECONDS)
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise ValueError(f"AskSage API error (HTTP {status_code}): {exc}") from exc
        except requests.RequestException as exc:
            if attempt < MAX_HTTP_RETRIES - 1:
                logger.warning("AskSage request failed (%s), retrying...", exc)
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise ValueError(f"AskSage request failed after {MAX_HTTP_RETRIES} attempts: {exc}") from exc
    else:
        raise ValueError("AskSage: exhausted retries")
```

**Why this is the right scope:**

- The core eval loop in `evaluate_translation()` catches all exceptions from `call_llm()`
  and records them as `overall_status = "ERROR"` with `error_message`. HTTP retries at
  the `call_llm()` level prevent transient 429s from producing ERROR results — the
  distinction matters for paper statistics (ERROR results are excluded from denominators).
- Retrying 429s here is fundamentally different from the self-repair loop. Self-repair is
  a deliberate evaluation protocol choice (models get 3 attempts to fix build failures).
  HTTP retries are transparent infrastructure — they should not appear in the result JSON
  as additional "attempts".
- The existing providers do not retry because the OpenAI SDK handles retries internally.
  AskSage requires `requests`, so this logic must be explicit.

**Dependency note:** `requests` is not currently in `requirements.txt`. Add it there and
to `requirements-lock.txt` once the AskSage branch is implemented. Alternatively, use
`httpx` (already installed as a transitive dependency via the `anthropic` SDK — check with
`pip show httpx`) to avoid adding a new dependency.

---

## Campaign 1 vs. Campaign 2: Architectural Divergence

### What Each Campaign Is

**Campaign 1 (existing, complete for Qwen):**
- `temperature=0.0` (deterministic, greedy)
- `max_retries=3` (self-repair on BUILD_FAIL — each retry adds a repair turn to the conversation)
- `augment_level=0..4` (L0 through L4 augmentation)
- Result naming: `{src}-to-{tgt}[-L{n}].json` (no sample tag)
- Metric: pass@1 (single attempt with repair)

**Campaign 2 (pending):**
- `temperature=0.7` (stochastic sampling)
- `max_retries=1` (single-shot, zero repair)
- `augment_level=0` (L0 only — no augmentation variants)
- `num_samples=3` (three independent samples per task)
- Result naming: `{src}-to-{tgt}-s{0,1,2}.json` (sample tag already implemented in `_result_path()`)
- Metric: pass@k (k=3 — any of the 3 samples passes)

### Configuration Surface

Both campaigns share:
- The same `evaluate_translation()` function signature (all campaign parameters are existing args)
- The same result JSON schema (`sample_id` and `num_samples` fields already exist in result JSON)
- The same `_result_path()` naming logic (sample tag already gated on `num_samples > 1`)
- The same provider dispatch in `call_llm()` (temperature is already a parameter)
- The same harness pipeline (build/run/verify is campaign-agnostic)

They diverge only at:
- **CLI invocation level:** `--max-retries 1 --num-samples 3 --temperature 0.7 --augment-levels 0`
- **Analysis level:** `analyze_eval.py` must compute pass@k instead of pass@1
  - pass@k = 1 - P(all k samples fail) — standard unbiased estimator from Chen et al. 2021
  - Requires grouping result JSONs by (src, tgt, model) and computing the k-sample estimate
  - This is an analysis-layer concern, not an evaluation-layer concern

**Critical finding:** Campaign 2 requires NO new pipeline code — the parameters already exist.
The only new code needed is:
1. A `pass@k` aggregation function in `analyze_eval.py` (or a companion `analyze_passatk.py`)
2. An `elif model.startswith("asksage-")` branch in `call_llm()`
3. A batch shell script in `scripts/batch/` with the Campaign 2 flags

The `num_samples` loop in `run_eval_batch.py` (line 109: `for sid in range(num_samples)`)
already handles generating `s0`, `s1`, `s2` result files for Campaign 2. The `--resume` flag
already skips existing sample files.

### What Would Break Campaign Isolation

The two campaigns MUST produce separate result directories or use non-colliding filenames.
Current naming:
- Campaign 1, L0: `results/evaluation/{model}/{src}-to-{tgt}.json`
- Campaign 1, L1: `results/evaluation/{model}/{src}-to-{tgt}-L1.json`
- Campaign 2, s0: `results/evaluation/{model}/{src}-to-{tgt}-s0.json`

The sample tag (`-s0`) and level tag (`-L1`) are mutually exclusive in the current naming.
Campaign 2 is L0-only, so `{src}-to-{tgt}-s0.json` never collides with Campaign 1 filenames.
This is safe as long as Campaign 2 runs are always invoked with `--augment-levels 0`.

---

## Suggested Build Order

Build in this order to maximize testability at each step:

1. **MODEL_REGISTRY entry for AskSage** — add the entry dict, run `--list-models` to verify.
   No live API call needed. Verifies registry lookup path. (~10 lines)

2. **Bare `elif` branch that raises `NotImplementedError`** — wire the model prefix into
   `call_llm()` so that unknown-provider error no longer fires for `asksage-*` models.
   Run `--dry-run` to confirm the branch is reached without hitting the API. (~5 lines)

3. **HTTP POST with defensive response parsing** — implement the actual `requests.post()`
   call, the token extraction fallbacks, and the normalized return dict. Test with a single
   live call using `python3 scripts/evaluation/llm_evaluate.py --source ... --target ...
   --model asksage-{model} --project-root ... -v` (no `--dry-run`). Log full raw response
   to confirm field names. (~40 lines)

4. **Harden field extraction** after researcher confirms response schema. Replace defensive
   `or` fallbacks with direct field access. Add an assertion or validation check.

5. **Campaign 2 pass@k aggregation** — add `compute_pass_at_k()` to `analyze_eval.py`.
   This is independent of AskSage and can be built in parallel once the result JSON schema
   for `num_samples > 1` is confirmed working.

6. **Campaign 2 batch script** — `scripts/batch/run_campaign2.sh` with the correct flags.
   Run against a 2-3 kernel subset first to validate end-to-end.

---

## Test Seams

### Seam 1: `call_llm()` — injectable via monkeypatching in tests

`call_llm()` is a module-level function. In tests, replace it with a fixture:

```python
# tests/test_asksage_adapter.py
import scripts.evaluation.llm_evaluate as llm_eval

def test_asksage_response_parsing(monkeypatch):
    """Verify defensive extraction handles missing token fields."""
    import requests

    class FakeResponse:
        status_code = 200
        def raise_for_status(self): pass
        def json(self):
            return {"response": "translated code here"}  # no usage field

    def fake_post(url, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)
    result = llm_eval.call_llm(
        model="asksage-testmodel",
        system_msg="translate",
        messages=[{"role": "user", "content": "code"}],
    )
    assert result["response_text"] == "translated code here"
    assert result["prompt_tokens"] == 0       # fallback
    assert result["completion_tokens"] == 0   # fallback
    assert result["finish_reason"] == "stop"  # fallback
```

### Seam 2: `evaluate_translation()` — injectable via `call_llm` mock

The entire `evaluate_translation()` function calls `call_llm()` exactly once per attempt
(line 1516). In integration tests for the Campaign 2 pass@k logic, mock `call_llm` to
return deterministic responses:

```python
def mock_call_llm(model, system_msg, messages, verbose=False, temperature=0.0):
    # Return a response that will PASS verification for the target spec
    return {
        "response_text": KNOWN_GOOD_TRANSLATION,
        "prompt_tokens": 100,
        "completion_tokens": 200,
        "finish_reason": "stop",
        "duration_seconds": 0.1,
    }
```

This seam lets you test the retry/repair loop, the sample_id naming, and the result JSON
schema without touching the LLM or the build system.

### Seam 3: HTTP layer — injectable via `requests` mock or `responses` library

For unit tests of the AskSage HTTP logic (rate limit retry, 429 handling, network timeout),
use the `responses` library (a lightweight `requests` mock) or pytest's `monkeypatch` on
`requests.post`. This seam is entirely inside the `elif asksage-` branch.

### Seam 4: `analyze_eval.py` pass@k — pure function, no side effects

The pass@k aggregation function takes a list of result dicts (loaded from JSON) and returns
a float. It has no I/O dependency and is testable with `pytest` directly against a list of
hardcoded result dicts:

```python
results = [
    {"overall_status": "PASS",  "sample_id": 0},
    {"overall_status": "BUILD_FAIL", "sample_id": 1},
    {"overall_status": "PASS",  "sample_id": 2},
]
assert compute_pass_at_k(results, k=3) > 0.0
assert compute_pass_at_k([{"overall_status": "BUILD_FAIL"}] * 3, k=3) == 0.0
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Abstract `LLMProvider` base class

**What:** Creating an `ABC` or `Protocol` for `LLMProvider` with a `call()` method, then
making each provider a subclass.

**Why bad:** The pipeline has one caller (`call_llm()`) and six concrete implementations
that differ in 15–30 lines each. An ABC adds ~50 lines of interface definition, a module
import graph, and forces all six existing providers to be refactored before AskSage works.
The abstraction earns its cost only when there are multiple callers with different injection
points — there is one caller here.

**Instead:** Add one `elif` branch. The existing structure IS the strategy pattern; the
dispatch function IS the context object.

### Anti-Pattern 2: Separate `scripts/evaluation/providers/` package

**What:** Moving all provider branches into individual files
(`providers/anthropic.py`, `providers/openai.py`, `providers/asksage.py`).

**Why bad:** Every existing provider is 15–30 lines. Moving them to separate files creates
6 new modules with 1 function each, and requires updating `call_llm()` to import and
dispatch to them. The cognitive overhead of cross-file navigation outweighs the benefit of
isolation at this scale.

**Threshold for reconsideration:** If a provider requires >100 lines of logic (e.g., OAuth2
token refresh, streaming response assembly, complex pagination), then a private helper
function in `llm_evaluate.py` (prefixed with `_call_asksage`) is appropriate. A separate
module file is not warranted until there are multiple callers or >200 lines per provider.

### Anti-Pattern 3: Storing raw provider responses in result JSONs

**What:** Adding a `provider_raw_response` field to the result JSON for debugging.

**Why bad:** Result JSONs are immutable. If a raw response field captures a schema version
that turns out to be wrong, correcting it would require re-running evaluations. The
`--verbose` logging approach (log raw response at DEBUG level, not in the result JSON) gives
the same debuggability without creating a result immutability problem.

### Anti-Pattern 4: Merging Campaign 1 and Campaign 2 into a "campaign" config object

**What:** Adding a `Campaign` dataclass with fields like `temperature`, `max_retries`,
`num_samples`, `augment_levels`, then passing it to `evaluate_translation()`.

**Why bad:** `evaluate_translation()` already accepts these as individual parameters.
Adding a wrapper dataclass adds an indirection layer without changing the semantics. The
CLI is the natural campaign configuration surface — shell scripts in `scripts/batch/` ARE
the campaign definitions. This is already how Campaign 1 works.

---

## Scalability Notes

These are not current concerns but worth flagging for the NeurIPS paper audit:

- **Result file count:** At 96 specs × 6 translation directions × 3 models × 3 Campaign 2
  samples = ~1,728 new result files. `analyze_eval.py` loads all result JSONs at startup via
  glob. At this scale (a few thousand files), glob + load is fast enough (~1–2s). No change
  needed.

- **AskSage throughput:** If AskSage rate limits are tighter than Together AI (~80k tokens/min),
  Campaign 2 runs (3 samples per task) will take proportionally longer. Use `tmux` for all
  runs >10 minutes. The existing `--resume` flag handles interrupted runs.

- **Token count gaps:** If AskSage never returns token counts, the `by_model` token usage
  table in `eval_summary.md` will show 0 for AskSage. Annotate this in the paper as a known
  limitation of the provider's API, not a pipeline defect.

---

## Sources

All findings are based on direct reading of the codebase (HIGH confidence):

- `scripts/evaluation/llm_evaluate.py` lines 730–1022 (call_llm dispatch)
- `scripts/evaluation/llm_evaluate.py` lines 1337–1416 (evaluate_translation signature)
- `scripts/evaluation/run_eval_batch.py` lines 57–200 (task building, num_samples loop)
- `.planning/codebase/ARCHITECTURE.md` (pipeline layer documentation)
- `.planning/PROJECT.md` (campaign definitions, AskSage status)

No external sources consulted — the architecture question is answered entirely by the
existing code structure.
