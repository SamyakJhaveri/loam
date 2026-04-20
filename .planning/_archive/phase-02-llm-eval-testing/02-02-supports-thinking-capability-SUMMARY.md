---
phase: 02-llm-eval-testing
plan: 02-02
subsystem: evaluation
tags: [model-registry, typed-dict, thinking-capability, d-04, d-05]
requires:
  - 02-01  # azure-gpt-5.4 entry must already exist (it did; `supports_thinking=True` was preserved)
provides:
  - "MODEL_REGISTRY[model]['supports_thinking']: bool — single source of truth for thinking capability"
  - "ModelRegistryEntry TypedDict (scripts/evaluation/llm_evaluate.py:61)"
  - "tests/test_model_registry.py — 5 always-on invariant tests"
affects:
  - 02-03  # will consume MODEL_REGISTRY[model]['supports_thinking'] for CLI flag wiring
  - 02-04  # will purge transient gpt-4.1-* entries; must update EXPECTED_THINKERS_POST_02_02 anchor
tech-stack:
  added: []
  patterns:
    - "TypedDict(total=False) + NotRequired for optional fields (typing stdlib)"
key-files:
  created:
    - tests/test_model_registry.py
  modified:
    - scripts/evaluation/llm_evaluate.py
decisions:
  - "Used TypedDict(total=False) with explicit NotRequired on api_model — keeps the diff minimal; runtime still treats provider/supports_thinking/notes as required via existing code paths and the pytest invariants."
  - "Followed PLAN.md (not CONTEXT.md D-04) for gpt-4.1-* transient entries: both receive supports_thinking=True. The PLAN.md objective line 43, step-4 whitelist line 95, and verification §2 (expect 6 thinkers) are internally consistent. CONTEXT.md D-04 line 40 says False for the same entries — PLAN.md is the authoritative executable."
  - "Plan acceptance criterion says 4 pytest functions; plan's own code has 5 (includes test_registry_is_nonempty). Implemented verbatim — 5/5 pass."
  - "Removed unused `import pytest` from test file (nothing decorates with pytest APIs). Not a deviation — the plan's suggested code imports pytest but never uses it."
metrics:
  duration_minutes: 8
  tasks_total: 2
  tasks_complete: 2
  files_created: 1
  files_modified: 1
  commits: 2
  completed_date: 2026-04-17
---

# Phase 2 Plan 02-02: supports_thinking Capability Summary

Widened `MODEL_REGISTRY` to a `TypedDict`-based schema and added `supports_thinking: bool` to every entry, with an always-on test file enforcing the shape.

## Objective Met

> Add `supports_thinking: bool` to every `MODEL_REGISTRY` entry, widen the value annotation to a `TypedDict`, and add `tests/test_model_registry.py` asserting the field + D-04 whitelist.

Result: `len(MODEL_REGISTRY) == 14`, 6 thinkers (`azure-gpt-5.4`, `azure-gpt-4.1`, `gpt-4.1-2025-04-14`, `o3-2025-04-16`, `o4-mini-2025-04-16`, `together-qwen-3.5-397b-a17b`). Every entry carries `supports_thinking`. 5 pytest tests pass.

## Artifacts

| Path | Kind | Lines |
|------|------|-------|
| `scripts/evaluation/llm_evaluate.py` | modified | +22 / −2 |
| `tests/test_model_registry.py` | created | +77 |

`ModelRegistryEntry` TypedDict inserted at `scripts/evaluation/llm_evaluate.py:61-65`; `MODEL_REGISTRY` annotation now `dict[str, ModelRegistryEntry]` at line 68. Import widened at line 45: `from typing import Any, NotRequired, TypedDict`.

## Entry Counts

- **Total registry entries:** 14
- **Thinkers (supports_thinking=True):** 6
- **Non-thinkers (supports_thinking=False):** 8

## Commits

| Task | Hash | Message |
|------|------|---------|
| 1 | `2be6257` | `feat(02-02): widen MODEL_REGISTRY to TypedDict + add supports_thinking` |
| 2 | `14b5a39` | `test(02-02): add tests/test_model_registry.py enforcing D-04/D-05` |

## Verification (from PLAN.md §verification)

- `pytest tests/test_model_registry.py -v` → **5/5 PASS** (plan expected 4; plan's own code defines 5).
- `python3 -c "... sum(1 for v in MODEL_REGISTRY.values() if v['supports_thinking'])"` → **6** (expected 6).
- `git diff --stat` over the two commits → only `scripts/evaluation/llm_evaluate.py` and `tests/test_model_registry.py` touched.

## Deviations from Plan

**None — plan executed as written.**

Minor clarifications (not deviations):

1. **Plan said "4 tests passing"; code has 5.** The plan's own `<action>` block defines `test_every_entry_has_supports_thinking`, `test_every_supports_thinking_is_bool`, `test_thinking_whitelist_matches_d04`, `test_no_startswith_thinking_branching`, AND `test_registry_is_nonempty` — five functions. I kept all 5. 5/5 pass.
2. **Plan said `gpt-4.1-mini` is in the registry and should get `supports_thinking=False`.** That key is not present in the current registry (dropped earlier; possibly by plan 02-01 or earlier cleanup). Nothing to do. The plan's mention is stale text; does not block any acceptance criterion.
3. **Regex-literal escape fix in the test file.** The plan's heredoc embeds `r"model\\.startswith\\([^)]+\\)"` (double-backslash, because it is itself inside an XML escaped heredoc). The correct Python literal is `r"model\.startswith\([^)]+\)"` (single backslash). I wrote the correct single-backslash form, which is what the plan clearly intended — a double-backslash raw string would fail to match `.startswith(...)`.
4. **Removed unused `import pytest`** from the test file — nothing in the body uses `pytest.` APIs. Ruff/linting hygiene; zero behavioral effect.

## Auth Gates

None.

## Byte-Stability Check (Azure/Gemini call sites)

Acceptance criterion: "Line 878 and line 956 are byte-for-byte unchanged vs. the 02-01 commit." After the TypedDict insertion and the 13 new `supports_thinking` fields, absolute line numbers shifted by +20. The **textual content** of both semantic call sites is unchanged:

- Azure `full_messages` construction: now at line 898 (was 878).
- Gemini `reasoning_effort="none"` call: now at line 981 (was 956).

`git diff 71c7957 HEAD -- scripts/evaluation/llm_evaluate.py` shows zero diff outside the MODEL_REGISTRY block + the typing import.

## Follow-ups (tracked for 02-04)

- When 02-04 purges `gpt-4.1-2025-04-14` and `azure-gpt-4.1`, update `EXPECTED_THINKERS_POST_02_02` in `tests/test_model_registry.py:17-24` to drop those two keys. The comment in the file anchors this action.
- 02-03 will consume `MODEL_REGISTRY[model]["supports_thinking"]` directly at the Qwen `enable_thinking` site (`llm_evaluate.py:1010` region per CONTEXT.md) and at the Azure `client_az.chat.completions.create(...)` site (line 883, NOT the Gemini line at 981 per CONTEXT.md "specifics" §line-discipline warning).

## Self-Check: PASSED

- FOUND: `scripts/evaluation/llm_evaluate.py` (modified, TypedDict at :61, 6 thinkers confirmed)
- FOUND: `tests/test_model_registry.py` (created, 5 tests pass)
- FOUND: commit `2be6257` (feat — Task 1)
- FOUND: commit `14b5a39` (test — Task 2)
