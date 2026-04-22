# Community 17

> 48 nodes

## Key Concepts

- **call_llm()** (15 connections) — `scripts/evaluation/llm_evaluate.py`
- **test_thinking_flag.py** (15 connections) — `tests/test_thinking_flag.py`
- **test_sampling_reproducibility.py** (14 connections) — `tests/test_sampling_reproducibility.py`
- **_capturing_openai_factory()** (8 connections) — `tests/test_sampling_reproducibility.py`
- **_derive_llm_seed()** (7 connections) — `scripts/evaluation/llm_evaluate.py`
- **test_azure_reasoning_omits_temperature_and_top_p()** (4 connections) — `tests/test_sampling_reproducibility.py`
- **_make_capturing_openai_factory()** (4 connections) — `tests/test_thinking_flag.py`
- **test_qwen_thinking_on_sets_enable_thinking_true()** (4 connections) — `tests/test_thinking_flag.py`
- **test_qwen_thinking_off_sets_enable_thinking_false()** (4 connections) — `tests/test_thinking_flag.py`
- **_make_azure_factory()** (4 connections) — `tests/test_thinking_flag.py`
- **test_azure_thinking_on_injects_reasoning_effort_medium()** (4 connections) — `tests/test_thinking_flag.py`
- **test_azure_thinking_off_omits_reasoning_effort()** (4 connections) — `tests/test_thinking_flag.py`
- **test_together_call_includes_seed_and_top_p()** (3 connections) — `tests/test_sampling_reproducibility.py`
- **test_together_call_omits_seed_when_none()** (3 connections) — `tests/test_sampling_reproducibility.py`
- **test_azure_reasoning_includes_seed()** (3 connections) — `tests/test_sampling_reproducibility.py`
- **test_azure_reasoning_omits_seed_when_none()** (3 connections) — `tests/test_sampling_reproducibility.py`
- **test_openai_reasoning_model_omits_top_p_and_temperature()** (3 connections) — `tests/test_sampling_reproducibility.py`
- **test_openai_nonreasoning_model_includes_top_p()** (3 connections) — `tests/test_sampling_reproducibility.py`
- **test_noncapable_claude_does_not_send_reasoning_kwargs()** (3 connections) — `tests/test_thinking_flag.py`
- **test_derive_llm_seed_deterministic_same_inputs()** (2 connections) — `tests/test_sampling_reproducibility.py`
- **test_derive_llm_seed_differs_across_sample_ids()** (2 connections) — `tests/test_sampling_reproducibility.py`
- **test_derive_llm_seed_differs_across_spec_pair()** (2 connections) — `tests/test_sampling_reproducibility.py`
- **test_derive_llm_seed_in_31bit_range()** (2 connections) — `tests/test_sampling_reproducibility.py`
- **_mock_chat_response()** (2 connections) — `tests/test_thinking_flag.py`
- **test_registry_azure_gpt_5_4_is_thinking_capable()** (2 connections) — `tests/test_thinking_flag.py`
- *... and 23 more nodes in this community*

## Relationships

- [[Community 0]] (6 shared connections)

## Source Files

- `scripts/evaluation/llm_evaluate.py`
- `tests/test_sampling_reproducibility.py`
- `tests/test_thinking_flag.py`

## Audit Trail

- EXTRACTED: 116 (78%)
- INFERRED: 32 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*