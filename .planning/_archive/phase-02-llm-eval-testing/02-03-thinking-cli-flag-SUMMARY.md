---
phase: 02-llm-eval-testing
plan: 03
subsystem: evaluation
tags: [cli, thinking, reasoning_effort, schema-bump]
dependency_graph:
  requires: [02-01, 02-02]
  provides:
    - "--thinking on|off CLI surface for llm_evaluate.py + run_eval_batch.py"
    - "thinking_enabled + num_samples result-JSON top-level fields"
  affects:
    - scripts/evaluation/llm_evaluate.py
    - scripts/evaluation/run_eval_batch.py
    - .claude/rules/evaluation.md
    - tests/test_thinking_flag.py
tech_stack:
  added: []
  patterns:
    - "Capability-gated CLI flag (--thinking) resolved against MODEL_REGISTRY[model]['supports_thinking']"
    - "Mocked-SDK unit tests via sys.modules patching (no real API calls)"
    - "Source-level regression guards (grep-style assertions embedded in pytest)"
key_files:
  created:
    - tests/test_thinking_flag.py
  modified:
    - scripts/evaluation/llm_evaluate.py
    - scripts/evaluation/run_eval_batch.py
    - .claude/rules/evaluation.md
decisions:
  - "--thinking is a string choice ('on' | 'off'), not a boolean flag — matches plan D-06/D-07 and keeps symmetry with future 'auto' modes."
  - "thinking_enabled is computed once per evaluate_translation() call; downstream code reads the boolean, not the CLI string."
  - "No helper extraction (_call_qwen_once / _call_azure_once). Mocked-SDK unit tests work against call_llm() directly — the plan explicitly permits this via the 'Alternative (allowed)' path."
  - "Non-thinking-capable models use DEBUG logging (not INFO) for the no-op trace, per plan D-08 / Claude's-discretion line."
  - "Azure call site is currently at llm_evaluate.py:905 (not :878 as the plan pre-text cites). Grep-result is authoritative per plan Step-1 — the plan already anticipates drift."
  - "Gemini reasoning_effort='none' safety line is currently at :979 (not :956 as the plan pre-text cites). Verified byte-identical pre/post plan via git diff."
metrics:
  duration_minutes: 12
  completed_date: 2026-04-17
---

# Phase 2 Plan 03: `--thinking` CLI Flag Summary

Added `--thinking on|off` flag (default `on`) to both `llm_evaluate.py` and
`run_eval_batch.py`, capability-gated via `MODEL_REGISTRY[model]['supports_thinking']`.
Qwen extra_body and Azure `reasoning_effort` kwargs are now driven by the flag instead
of hardcoded; Gemini's unrelated `reasoning_effort="none"` safety line is untouched.
Result JSONs gain two new top-level fields (`thinking_enabled`, `num_samples`) for
downstream canonical/ablation filtering and pass@k reconstruction. Schema bump is
documented in `.claude/rules/evaluation.md`.

## Final Azure Call-Site Line Number (grep result)

Task 1 Step 5 required re-verification via grep. Current state (post-edit):

```
grep -n 'client_az.chat.completions.create' scripts/evaluation/llm_evaluate.py
→ 905:        response = client_az.chat.completions.create(... )
```

The plan text referenced `:878`; actual live line is `:905`. The `reasoning_effort="medium"`
assignment itself lives at `:915` inside the conditional `_az_kwargs` build. Acceptable
per plan's explicit "grep result is authoritative" guidance (plan 02-03 §Step 1).

## Gemini `reasoning_effort="none"` — Byte-Identical

The Gemini safety line (plan references `:956`; live `:979`) was verified byte-identical
pre/post edit:

```
grep -n 'reasoning_effort="none"' scripts/evaluation/llm_evaluate.py
→ 979:            reasoning_effort="none",
```

`git diff scripts/evaluation/llm_evaluate.py` shows no change within the Gemini branch
(`elif model.startswith("gemini-")`). The surrounding comment at `:986-988` is also
untouched. The D-10 discipline is enforced and tested by
`tests/test_thinking_flag.py::test_source_gemini_reasoning_effort_none_unchanged`.

## Two New Result-JSON Top-Level Fields

Added at `llm_evaluate.py:1858-1859` inside the `result: dict[str, Any]` literal:

```python
"thinking_enabled": thinking_enabled,  # resolved: flag × supports_thinking capability
"num_samples": num_samples,            # k in pass@k (default 1 single-task)
```

Both fields are authored once, from kwargs flowing through `evaluate_translation()`.
`num_samples` defaults to 1 (single-task CLI); `run_eval_batch.py` overrides with
`args.num_samples` from its existing `--num-samples` flag. `thinking_enabled` is
derived as `(thinking == "on") and MODEL_REGISTRY.get(model, {}).get("supports_thinking", False)`.

## Wire Diagram

```
llm_evaluate.py --thinking flag ──┐
                                  ▼
                       evaluate_translation(thinking="on"|"off")
                                  │
                                  ▼
                       thinking_enabled = flag × capability
                          │        │
                          ▼        ▼
              ┌── call_llm(thinking_enabled) ──┐
              │         (dispatched by provider)│
              │                                 │
     ┌────────┤                                 ├─────────┐
     │ Qwen   │                                 │  Azure  │
     │ extra_body.enable_thinking=X             │  kwargs.reasoning_effort="medium" if X
     └────────┘                                 └─────────┘

run_eval_batch.py --thinking ──→ run_batch(thinking=...)
                             └──→ evaluate_translation(..., thinking=...)
                                    │
                                    ▼
                        result.thinking_enabled + result.num_samples
```

## Deviations from Plan

1. **[Rule 0 — Surface-level reference] Line-number drift.** Plan text cited `:878` (Azure)
   and `:956` (Gemini). Live grep returns `:905` and `:979` respectively. The plan explicitly
   anticipates this (Step 1 — "treat the grep result as authoritative") so this is not a
   behavioural deviation. The SUMMARY records the live values.

2. **[Rule 0 — Test structure] Tests did NOT use helper extraction.** Plan Task 3 offered two
   alternatives: (a) extract private `_call_qwen_once` / `_call_azure_once` helpers and test
   them, or (b) write source-level grep tests + direct `call_llm()` mocking. Chose (b) because
   it keeps diff minimal and doesn't introduce new module surface. The plan explicitly permits
   this: "Alternative (allowed): …". All 6 plan-specified behaviours are covered (Qwen on/off,
   Azure on/off, non-capable no-op, result-JSON fields) — plus 3 additional source-level
   regression guards.

3. **Added `--num-samples` to `llm_evaluate.py` CLI.** The plan says "Add `num_samples: int = 1`
   kwarg to `evaluate_translation()`" but does not require the single-task CLI flag. Added
   the flag anyway for symmetry with `run_eval_batch.py` — otherwise there's no way to set
   the result-JSON `num_samples` field from the single-task CLI. Minimal addition (one
   argparse block, one call-site kwarg), doesn't expand scope.

4. **Added `thinking` to batch summary JSON + console announce line.** Minor observability
   addition in `run_eval_batch.py` (one key in the summary dict, one f-string entry in the
   announce print). Matches the existing pattern for `temperature` and `num_samples`.

## Tests

- `pytest tests/test_thinking_flag.py -v` → **11/11 PASS** (0.02s)
- `pytest tests/test_model_registry.py -q` → **5/5 PASS** (prior plan, still green)
- `pytest tests/ -m "not integration and not llm" -q` → **139 passed, 3 skipped**
  (full unit suite, no regressions)

## Known Stubs

None. The flag is fully wired end-to-end (CLI → `evaluate_translation` → `call_llm`
→ per-provider SDK kwargs → result-JSON fields) with unit-test coverage on every branch.

## Self-Check: PASSED

- `scripts/evaluation/llm_evaluate.py` modified — `--thinking` flag present in argparse,
  `thinking_enabled` computed in `evaluate_translation`, Qwen + Azure call sites use the
  computed boolean, `thinking_enabled` + `num_samples` in result JSON. Gemini line untouched.
- `scripts/evaluation/run_eval_batch.py` modified — `--thinking` flag present, plumbed
  through `run_batch` → `evaluate_translation`, recorded in batch summary.
- `.claude/rules/evaluation.md` — new "Result JSON Schema" + "CLI flag: `--thinking`" sections
  documenting the schema bump + the `:878`/`:956` line-discipline note.
- `tests/test_thinking_flag.py` — 11 tests, all pass.
- All acceptance criteria grep checks from the plan return the expected matches.
- `python3 scripts/evaluation/llm_evaluate.py --help | grep -- '--thinking'` → present.
- `python3 scripts/evaluation/run_eval_batch.py --help | grep -- '--thinking'` → present.
