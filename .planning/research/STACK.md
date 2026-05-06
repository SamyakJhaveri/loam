# Technology Stack — Milestone 2 Additions

**Project:** ParBench
**Scope:** Additions only — TDD layer, AskSage adapter, Campaign 2 pipeline
**Researched:** 2026-04-09
**Existing stack:** See `.planning/codebase/STACK.md` (authoritative for everything already in use)

---

## Research Questions Answered

1. TDD of Python data/eval pipelines (pytest patterns, fixtures, mocking LLM APIs)
2. HTTP client for integrating AskSage (non-OpenAI-native endpoint, unknown response schema)
3. Testing subprocess-heavy code (harness executes `subprocess.run` via builder.py and runner.py)

---

## Decision Summary (TL;DR for Roadmap)

| Area | Recommendation | Confidence |
|------|---------------|------------|
| Test mocking | `pytest-mock` 3.15.1 (mocker fixture) | HIGH |
| HTTP mocking | `respx` 0.23.1 (httpx-native) | HIGH |
| Subprocess mocking | `pytest-subprocess` 1.5.4 | HIGH |
| Async test support | `pytest-asyncio` 1.3.0, `auto` mode | HIGH |
| AskSage adapter strategy | OpenAI-compat endpoint (`base_url` swap) as primary, native `/server/query` as fallback | HIGH |
| HTTP client for native endpoint | `httpx` 0.28.1 (already installed, sync client) | HIGH |
| conftest structure | Hierarchical: `tests/conftest.py` + per-suite fixtures | HIGH |

---

## 1. TDD: pytest Patterns for Data/Eval Pipelines

### Core: pytest 9.0.2 (already installed)

**Use:** Already present. No upgrade needed. Version 9.x has stable parametrize, fixture scoping, and conftest discovery.

**Pattern: conftest.py hierarchy**

Use a two-level fixture hierarchy:

- `tests/conftest.py` — session-scoped fixtures: project_root path, sample spec dicts loaded from disk once, shared mock LLM response strings
- `tests/test_*/conftest.py` — module-scoped fixtures specific to harness vs. eval vs. analysis tests

Rationale: the spec JSONs and result JSONs are expensive to load and immutable; session scope avoids re-reading them per test. Function scope for mocks that track call counts (those must reset between tests).

**Pattern: fixture parametrization for pipeline stages**

Each pipeline stage (build, run, verify) has discrete inputs and outputs expressed as pydantic models (`BuildResult`, `RunResult`). Test each stage in isolation by constructing the input model directly, not by running the full pipeline. Use `@pytest.mark.parametrize` to drive known-good and known-fail spec cases.

**Pattern: conftest fixtures for spec loading**

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def sample_spec(project_root):
    """Canonical BFS CUDA spec — used across multiple test modules."""
    spec_path = project_root / "specs" / "rodinia-bfs-cuda.json"
    return json.loads(spec_path.read_text())
```

Load real specs from disk in session fixtures. Do NOT hard-code spec dicts inline in tests — the real JSONs are the source of truth and should be exercised.

### Mock Library: pytest-mock 3.15.1 (NEW — add to dev deps)

**Install:** `python3 -m pip install pytest-mock==3.15.1`

**Why pytest-mock over bare unittest.mock:**
- `mocker` fixture (injected by pytest) auto-resets after every test; no manual `patch.stop()` or `@patch` decorator juggling
- Integrates with pytest introspection for clearer assertion failures (`mocker.spy`, `mocker.stub`)
- Scoped patching avoids state leakage between tests — critical when `call_llm()` is patched globally

**How to mock `call_llm` in eval pipeline tests:**

```python
def test_evaluate_translation_build_fail(mocker, sample_spec, project_root):
    mocker.patch(
        "scripts.evaluation.llm_evaluate.call_llm",
        return_value="```cpp\n// intentionally broken\n```",
    )
    result = evaluate_translation(...)
    assert result["overall_status"] == "BUILD_FAIL"
```

**Do NOT use:** Raw `@unittest.mock.patch` decorators. They require manual cleanup and produce harder-to-read failure messages. pytest-mock strictly supersedes them for pytest-based tests.

---

## 2. HTTP Client: AskSage Adapter

### Critical Finding: AskSage Has Two Endpoints

Research confirmed AskSage exposes two distinct interfaces:

| Endpoint | Format | Auth header | SDK compatibility |
|----------|--------|------------|-------------------|
| `POST /server/openai/v1/chat/completions` | OpenAI-compatible | `Authorization: Bearer <key>` | openai SDK, base_url swap |
| `POST /server/query` | Native AskSage | `x-access-tokens: <key>` | httpx only (custom) |

The OpenAI-compatible endpoint is functionally identical to the OpenAI API with only the base URL changed. The existing dispatch pattern in `call_llm()` already handles this pattern (see groq, gemini, together branches — all use `openai.OpenAI(api_key=..., base_url=...)`).

### Recommended Adapter Strategy: OpenAI-compat first, native as fallback

**Primary path:** Add an `asksage-*` branch to `call_llm()` that instantiates:

```python
client = openai.OpenAI(
    api_key=os.environ["ASKSAGE_API_KEY"],
    base_url="https://api.asksage.ai/server/openai/v1",
)
```

This requires zero new HTTP client libraries and is immediately testable with respx (below). The `model` parameter is passed through as the AskSage model identifier.

**Why this is correct:** The AskSage OpenAI-compat endpoint follows the exact same API specification as OpenAI. The existing openai SDK 2.28.0 handles base_url routing natively.

**Fallback path (if Argonne constrains to native endpoint only):** Use `httpx` 0.28.1 (already installed as transitive dep of `anthropic` SDK). Do NOT add `requests` — httpx is already present, supports both sync and async, and is testable via `respx`.

**Native `/server/query` request shape (confirmed from official docs):**
```json
{
  "message": "<prompt text>",
  "model": "<model-id>",
  "temperature": 0.7,
  "limit_references": 0
}
```
Auth: `x-access-tokens: <key>` header (24-hour token or static API key).

**Native response shape (confirmed from official docs):**
```json
{
  "response": "<status>",
  "message": "<generated text>",
  "uuid": "<id>",
  "references": [...],
  "status": 200
}
```
The LLM-generated content lives at `response["message"]`, not `response["choices"][0]["message"]["content"]` as in OpenAI format. This is the key structural difference requiring a custom extractor if the native endpoint is used.

**Confidence on response schema:** MEDIUM. Official docs confirm the top-level shape. The exact structure of `references` and error responses requires empirical validation on a live call.

### HTTP Client for Native Endpoint: httpx 0.28.1 (already installed)

**Why httpx over requests:**
- Already installed (transitive dep of `anthropic` 0.85.0)
- Zero new dependency
- Supports both sync (`httpx.Client`) and async (`httpx.AsyncClient`) — consistent with future async eval pipeline work
- Mockable via `respx` (see below)

**Do NOT add:** `requests`, `aiohttp`. Adding `requests` is redundant (httpx is a strict superset for this use case). `aiohttp` is unnecessary — the eval pipeline is synchronous.

---

## 3. HTTP Mocking: respx 0.23.1 (NEW — add to dev deps)

**Install:** `python3 -m pip install respx==0.23.1`

**Why respx:**
- The only pytest-native HTTPX mock library. Works via `respx_mock` pytest fixture or `@respx.mock` decorator
- Handles arbitrary response bodies — no schema assumption. Configure any JSON dict as the response body
- Intercepts at the transport layer, not at the function level — tests the full httpx call chain
- Route matching by URL pattern, method, and headers — can assert that `x-access-tokens` header is present
- Supports `side_effect` for simulating error responses and retry scenarios
- Version 0.23.1 released 2026-04-08, Python 3.8+, httpx 0.25+

**Usage pattern for AskSage native endpoint:**

```python
import respx
import httpx

@respx.mock
def test_asksage_native_adapter():
    respx.post("https://api.asksage.ai/server/query").mock(
        return_value=httpx.Response(200, json={
            "response": "ok",
            "message": "```cpp\nint foo() { return 42; }\n```",
            "uuid": "abc123",
            "references": [],
            "status": 200,
        })
    )
    result = call_asksage_native(prompt="translate this", model="gpt-4o")
    assert "foo" in result
```

**Do NOT use:** `responses` (requests-only, incompatible with httpx), `pytest-httpserver` (full server process, heavier than needed), `unittest.mock.patch` on httpx internals (brittle, breaks on httpx version changes).

---

## 4. Subprocess Mocking: pytest-subprocess 1.5.4 (NEW — add to dev deps)

**Install:** `python3 -m pip install pytest-subprocess==1.5.4`

**Why this matters:** `harness/builder.py` and `harness/runner.py` call `subprocess.run(...)` directly. Unit tests for `build_spec()` and `run_spec()` must not invoke real compilers (nvcc, make) — those require the GPU machine, specific paths, and minutes of execution time.

**Why pytest-subprocess over manual patching:**
- `fake_process` fixture intercepts `subprocess.run`, `subprocess.Popen`, and `asyncio.create_subprocess_*` calls uniformly
- Register commands with specific return codes and stdout/stderr to simulate BUILD_FAIL, RUN_FAIL, VERIFY scenarios
- Version 1.5.4 (released 2026-03-21) explicitly supports asyncio subprocess
- Automatic cleanup between tests (pytest fixture lifecycle)

**Usage pattern for harness tests:**

```python
def test_build_spec_returns_build_fail_on_nonzero_exit(fake_process, sample_spec, project_root, tmp_path):
    fake_process.register_subprocess(
        fake_process.any(),  # match any build command
        returncode=1,
        stderr=b"error: 'texture' is not a member of namespace 'std'",
    )
    result = build_spec(sample_spec, project_root=project_root, work_dir=tmp_path)
    assert result.status.name == "BUILD_FAIL"
    assert "texture" in result.error_output
```

**Do NOT use:** Raw `unittest.mock.patch("subprocess.run", ...)`. This patches only the specific import path — if builder.py imports subprocess directly (it does), the patch target must be `harness.builder.subprocess.run`, which is fragile and breaks if the import is restructured. pytest-subprocess patches at the OS level.

---

## 5. Async Test Support: pytest-asyncio 1.3.0 (NEW — add to dev deps)

**Install:** `python3 -m pip install pytest-asyncio==1.3.0`

**When needed:** The eval pipeline is currently synchronous. However, if the AskSage adapter or Campaign 2 pass@k runner introduces async batching (e.g., concurrent LLM calls), tests for those components need pytest-asyncio.

**Configuration:** Add to `pyproject.toml` or `pytest.ini`:
```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

`auto` mode is recommended over `strict` for this project: it avoids requiring `@pytest.mark.asyncio` on every async test function, reducing boilerplate in a codebase where async is added incrementally.

**Important migration note:** pytest-asyncio 1.0+ removed the `event_loop` fixture. Any test that previously used `@pytest.fixture` to create a custom event loop must be updated to use `@pytest_asyncio.fixture` with an explicit `loop_scope` parameter.

**Confidence on necessity:** LOW. The current pipeline is synchronous. Include in dev deps now for future-proofing; mark async tests as `@pytest.mark.asyncio` even in auto mode for explicitness.

---

## 6. Test Infrastructure: conftest.py Structure

No conftest.py exists in `tests/` currently. Create:

```
tests/
  conftest.py                  # session-scoped: project_root, sample specs, result fixtures
  harness/
    conftest.py                # fake_process fixtures for build/run scenarios
    test_builder.py
    test_runner.py
    test_verifier.py
  evaluation/
    conftest.py                # mock call_llm, fake AskSage responses
    test_llm_evaluate.py
    test_run_eval_batch.py
  analysis/
    conftest.py                # pre-loaded result JSON fixtures
    test_analyze_eval.py
```

**Fixture scoping rules:**
- `scope="session"`: project_root path, spec JSON loading, immutable result JSON loading
- `scope="module"`: shared mock LLM response strings within a test module
- `scope="function"` (default): all mocker patches, fake_process registrations, tmp_path

---

## New Dependencies to Add

Add to `requirements.txt` under `[dev]` optional group in `pyproject.toml`:

```
pytest-mock>=3.15.1
pytest-subprocess>=1.5.4
pytest-asyncio>=1.3.0
respx>=0.23.1
```

No new runtime dependencies. `httpx` 0.28.1 is already installed.

---

## Alternatives Considered and Rejected

| Category | Rejected | Reason |
|----------|----------|--------|
| HTTP mocking | `responses` | requests-only; incompatible with httpx |
| HTTP mocking | `pytest-httpserver` | Spins up real TCP server; over-engineered for unit tests |
| Subprocess mocking | `unittest.mock.patch("subprocess.run")` | Import-path fragility; no asyncio subprocess support |
| LLM mocking | VCR.py / cassettes | Record-then-replay; LLM responses are non-deterministic, cassettes rot |
| AskSage client | Custom `requests` adapter | httpx already installed; requests adds a redundant dep |
| Async framework | `aiohttp` | Not needed; pipeline is synchronous; httpx covers the async-capable case if needed |
| Test framework | `unittest` | Inferior fixture scoping, parametrize, and plugin ecosystem vs. pytest |

---

## Sources

- AskSage official docs: [API Endpoints](https://docs.asksage.ai/docs/api-documentation/api-endpoints.html), [Server Parameters and Responses](https://docs.asksage.ai/docs/api-documentation/Server-Parameters-and-Responses.html), [OpenAI Compatibility Guide](https://docs.asksage.ai/docs/api-documentation/OpenAI-Compatibility-Guide.html)
- respx: [PyPI 0.23.1](https://pypi.org/project/respx/), [GitHub](https://github.com/lundberg/respx)
- pytest-subprocess: [PyPI 1.5.4](https://pypi.org/project/pytest-subprocess/), [Docs](https://pytest-subprocess.readthedocs.io/)
- pytest-mock: [PyPI 3.15.1](https://pypi.org/project/pytest-mock/)
- pytest-asyncio: [PyPI 1.3.0](https://pypi.org/project/pytest-asyncio/), [Stable Docs](https://pytest-asyncio.readthedocs.io/en/stable/)
- [HTTPX vs Requests 2025](https://www.morethanmonkeys.co.uk/article/comparing-requests-and-httpx-in-python-which-http-client-should-you-use-in-2025/)
- [Mocking subprocess with pytest-subprocess (Simon Willison)](https://til.simonwillison.net/pytest/pytest-subprocess)
- [respx pytest integration guide 2025](https://rogulski.it/blog/pytest-httpx-vcr-respx-remote-service-tests/)

---

*Research date: 2026-04-09*
