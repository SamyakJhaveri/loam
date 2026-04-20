---
phase: 02-llm-eval-testing
plan: 02
type: execute
wave: 2
depends_on:
  - "02-01"
files_modified:
  - scripts/evaluation/llm_evaluate.py
  - tests/test_model_registry.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "Every MODEL_REGISTRY entry carries a boolean `supports_thinking` field"
    - "Thinking-capable set matches D-04 whitelist exactly (including transient gpt-4.1-* entries at this stage)"
    - "Value type of MODEL_REGISTRY widens to a TypedDict-based schema with provider/supports_thinking/notes/api_model(optional)"
    - "No code path outside MODEL_REGISTRY uses `model.startswith(...)` to detect thinking capability (D-05)"
    - "test_model_registry.py enforces the shape on every commit"
  artifacts:
    - path: "scripts/evaluation/llm_evaluate.py"
      provides: "MODEL_REGISTRY with capability schema"
      contains: "supports_thinking"
    - path: "tests/test_model_registry.py"
      provides: "Assertions that every entry has supports_thinking + whitelist match"
      min_lines: 40
  key_links:
    - from: "MODEL_REGISTRY[model]['supports_thinking']"
      to: "Plan 02-03 thinking-flag branching"
      via: "Direct dict access (no startswith)"
      pattern: "MODEL_REGISTRY\\[.*\\]\\[['\\\"]supports_thinking['\\\"]\\]"
---

<objective>
Add a `supports_thinking: bool` capability field to every entry in `MODEL_REGISTRY`, widen the value-type annotation to a `TypedDict`-based schema, and add `tests/test_model_registry.py` asserting the field is present and the thinking whitelist matches D-04 exactly.

Purpose: Plan 02-03 branches on thinking capability at multiple call sites. Using a registry field (not `model.startswith(...)`) gives one source of truth for "can we toggle thinking" and prevents the class of bugs where a prefix check misclassifies a new model. 02-02 establishes that single source of truth so 02-03 can consume it.

Output: Schema-widened MODEL_REGISTRY + new test file enforcing the schema.

Implements D-04, D-05.

**Ordering note (from D-04):** At this commit, the transient entries `gpt-4.1-2025-04-14` and `azure-gpt-4.1` still exist in the registry — they receive `supports_thinking=True` here (both are reasoning-capable) and are removed by plan 02-04. `gpt-4.1-mini` also still exists and receives `supports_thinking=False`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-llm-eval-testing/02-CONTEXT.md
@.planning/phases/02-llm-eval-testing/02-01-SUMMARY.md
@scripts/evaluation/llm_evaluate.py
@tests/conftest.py
@.claude/rules/known-issues.md
@./CLAUDE.md
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Widen MODEL_REGISTRY schema to TypedDict + add supports_thinking to every entry</name>
  <files>scripts/evaluation/llm_evaluate.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-04, D-05)
    - scripts/evaluation/llm_evaluate.py (lines 1-120 for imports + MODEL_REGISTRY)
  </read_first>
  <behavior>
    - After edit, every entry in MODEL_REGISTRY (including transient `gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini` that will be purged in 02-04) has a `supports_thinking` boolean key.
    - `import typing` / `from typing import TypedDict, NotRequired` is added if not already present.
    - Registry value type is annotated as a `TypedDict` subclass with fields `provider: str`, `supports_thinking: bool`, `notes: str`, `api_model: NotRequired[str]`.
    - No runtime behavior changes. Existing code paths that read `entry["provider"]` etc. still work.
  </behavior>
  <action>
Edit `scripts/evaluation/llm_evaluate.py`:

1. **Imports:** Ensure `from typing import TypedDict` is imported near the top of the file (add `NotRequired` too — on Python 3.11+ it is in `typing`; this project targets Python 3.12 per CLAUDE.md so `typing.NotRequired` is available). If a `typing` import line already exists, extend it. Otherwise add `from typing import TypedDict, NotRequired` immediately after the existing stdlib imports.

2. **Define the TypedDict** ABOVE the `MODEL_REGISTRY` assignment (i.e., just before line 61). Use this exact definition:

```python
class ModelRegistryEntry(TypedDict, total=False):
    provider: str  # required at runtime
    supports_thinking: bool  # required at runtime
    notes: str  # required at runtime
    api_model: NotRequired[str]  # optional, used by together-qwen entry
```

Note: Using `total=False` lets us keep `api_model` optional while still annotating the required fields. Alternative allowed: `total=True` on a base class plus a second `total=False` class for optional fields. Pick whichever keeps the diff smallest. Do NOT use `Required[...]` (that idiom only helps with `total=False`; be consistent).

3. **Annotation change:** Change the annotation on the `MODEL_REGISTRY = { ... }` assignment from `dict[str, dict[str, str]]` to `dict[str, ModelRegistryEntry]`. If the current line has no explicit annotation, add `MODEL_REGISTRY: dict[str, ModelRegistryEntry] = {`.

4. **Add `supports_thinking` to every entry.** Per D-04:
   - `True` for: `azure-gpt-5.4` (already has it from 02-01; no change), `o3-2025-04-16`, `o4-mini-2025-04-16`, `together-qwen-3.5-397b-a17b`, `gpt-4.1-2025-04-14` (transient — purged in 02-04), `azure-gpt-4.1` (transient — purged in 02-04)
   - `False` for: Claude models (every `claude-*` key), `gpt-4o` (every `gpt-4o*` key), `gemini-2.5-*` (every `gemini-*` key), `groq-llama-3.3-70b-versatile`, `gpt-4.1-mini` (transient)

   Insert `"supports_thinking": True,` or `"supports_thinking": False,` as the **second** key in each entry (after `provider`, before `notes`/`api_model`). Keep comma discipline.

5. **Runtime helper robustness.** Grep for `.get(` usages on registry entries in `llm_evaluate.py` — existing helpers (`client_openai`, `client_az`, `client_together`) already tolerate missing keys. Do NOT refactor them. The TypedDict is purely for static checking.

6. **Do NOT modify `llm_evaluate.py:878` or `llm_evaluate.py:956`.** 02-03's scope.

7. **Do NOT add any `model.startswith(...)` thinking checks.** D-05 forbids them; 02-03 will consume `supports_thinking` directly.

8. **Do NOT touch any MODEL_REGISTRY key names** (the purge is 02-04's scope).
  </action>
  <verify>
    <automated>python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; missing = [k for k,v in MODEL_REGISTRY.items() if 'supports_thinking' not in v]; assert not missing, f'missing supports_thinking: {missing}'; print(f'OK: {len(MODEL_REGISTRY)} entries all carry supports_thinking')"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c '"supports_thinking"' scripts/evaluation/llm_evaluate.py` returns an integer equal to `len(MODEL_REGISTRY)` (every entry has it once).
    - `grep -n 'class ModelRegistryEntry' scripts/evaluation/llm_evaluate.py` returns exactly one line.
    - `grep -n 'TypedDict' scripts/evaluation/llm_evaluate.py` returns at least one import line and one class definition.
    - `grep -nE '\\.startswith\\(["\\']?(azure|o3|o4|together-qwen)' scripts/evaluation/llm_evaluate.py` returns no NEW matches vs. pre-edit (pre-existing startswith usage for provider dispatch at line 861 is permitted because it is NOT a thinking-capability check).
    - `python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; thinkers = {k for k,v in MODEL_REGISTRY.items() if v['supports_thinking']}; print(sorted(thinkers))"` output must include: `azure-gpt-4.1`, `azure-gpt-5.4`, `gpt-4.1-2025-04-14`, `o3-2025-04-16`, `o4-mini-2025-04-16`, `together-qwen-3.5-397b-a17b` and must NOT include any `claude-*`, `gpt-4o*`, `gemini-*`, `groq-*`, or `gpt-4.1-mini`.
    - Line 878 and line 956 are byte-for-byte unchanged vs. the 02-01 commit.
  </acceptance_criteria>
  <done>MODEL_REGISTRY annotated via TypedDict, every entry has boolean `supports_thinking`, whitelist matches D-04 exactly (with transient 4.1-* entries set per D-04 ordering note).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Add tests/test_model_registry.py enforcing the shape</name>
  <files>tests/test_model_registry.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-04, D-05)
    - tests/conftest.py (integration marker pattern)
    - scripts/evaluation/llm_evaluate.py (MODEL_REGISTRY post-edit from Task 1)
  </read_first>
  <behavior>
    - `test_every_entry_has_supports_thinking` fails if any entry is missing the key.
    - `test_every_supports_thinking_is_bool` fails if any value is non-bool.
    - `test_thinking_whitelist_matches_d04` asserts the exact post-edit thinking set (handles the transient `gpt-4.1-*` entries by using a set-membership check keyed on keys that may or may not exist yet).
    - `test_no_startswith_thinking_branching` greps the source of `llm_evaluate.py` to prove no `model.startswith(...)` call is followed (on the same line or next few lines) by thinking-related logic.
  </behavior>
  <action>
Create `tests/test_model_registry.py`:

```python
"""Phase 2 / Plan 02-02: MODEL_REGISTRY capability-field invariants.

Enforces D-04 (every entry has `supports_thinking: bool`) and D-05
(no `model.startswith(...)` thinking-capability branching).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.evaluation.llm_evaluate import MODEL_REGISTRY

LLM_EVAL_PATH = Path(__file__).parent.parent / "scripts" / "evaluation" / "llm_evaluate.py"

# Post-02-02 (pre-02-04) expected thinking-capable set.
# Once 02-04 purges gpt-4.1-*, run the same test under that plan's updated expected set.
EXPECTED_THINKERS_POST_02_02 = {
    "azure-gpt-5.4",
    "o3-2025-04-16",
    "o4-mini-2025-04-16",
    "together-qwen-3.5-397b-a17b",
    # Transient — removed in 02-04:
    "gpt-4.1-2025-04-14",
    "azure-gpt-4.1",
}


def test_every_entry_has_supports_thinking():
    missing = [k for k, v in MODEL_REGISTRY.items() if "supports_thinking" not in v]
    assert not missing, f"entries missing supports_thinking: {missing}"


def test_every_supports_thinking_is_bool():
    non_bool = {k: type(v["supports_thinking"]).__name__
                for k, v in MODEL_REGISTRY.items()
                if not isinstance(v["supports_thinking"], bool)}
    assert not non_bool, f"non-bool supports_thinking values: {non_bool}"


def test_thinking_whitelist_matches_d04():
    """Every key expected-thinker must be in the registry and set True.
    Every other registry entry must be False.
    """
    # All expected thinkers that exist must be True.
    for k in EXPECTED_THINKERS_POST_02_02:
        if k in MODEL_REGISTRY:
            assert MODEL_REGISTRY[k]["supports_thinking"] is True, \
                f"{k} must have supports_thinking=True per D-04"
    # Every other entry must be False.
    for k, v in MODEL_REGISTRY.items():
        if k not in EXPECTED_THINKERS_POST_02_02:
            assert v["supports_thinking"] is False, \
                f"{k} unexpectedly marked supports_thinking=True; update D-04 whitelist?"


def test_no_startswith_thinking_branching():
    """D-05: thinking-capability branches must query MODEL_REGISTRY[model]['supports_thinking'].
    No `model.startswith(...)` patterns may appear in the same line/block as reasoning_effort or enable_thinking."""
    src = LLM_EVAL_PATH.read_text()
    # Find every `model.startswith(...)` occurrence
    bad_patterns = []
    for match in re.finditer(r"model\\.startswith\\([^)]+\\)", src):
        # look at a 200-char window around the match
        start = max(0, match.start() - 100)
        end = min(len(src), match.end() + 200)
        window = src[start:end]
        if ("reasoning_effort" in window) or ("enable_thinking" in window):
            bad_patterns.append((match.group(0), window))
    assert not bad_patterns, (
        f"Found model.startswith(...) used near thinking-capability logic. "
        f"Use MODEL_REGISTRY[model]['supports_thinking'] instead. Offenders: "
        f"{[p[0] for p in bad_patterns]}"
    )


def test_registry_is_nonempty():
    assert len(MODEL_REGISTRY) > 0
```

Do NOT mark these tests with `@pytest.mark.integration` or `@pytest.mark.llm` — they are pure static checks over the imported dict + source file. They MUST run in the default `pytest tests/` invocation.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_model_registry.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/test_model_registry.py -v` exits 0 with 4 tests passing.
    - `grep -n '@pytest.mark.integration' tests/test_model_registry.py` returns no matches.
    - `grep -n '@pytest.mark.llm' tests/test_model_registry.py` returns no matches.
    - `grep -n 'EXPECTED_THINKERS_POST_02_02' tests/test_model_registry.py` returns matches (comment anchor for 02-04 to update).
  </acceptance_criteria>
  <done>New test file exists, all four tests pass, guards D-04 + D-05 invariants.</done>
</task>

</tasks>

<verification>
- `pytest tests/test_model_registry.py -v` passes 4/4.
- `python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; print(sum(1 for v in MODEL_REGISTRY.values() if v['supports_thinking']))"` returns 6 (azure-gpt-5.4, o3, o4-mini, together-qwen, gpt-4.1-2025-04-14, azure-gpt-4.1).
- `git diff --stat` shows only `scripts/evaluation/llm_evaluate.py` and `tests/test_model_registry.py`.
</verification>

<success_criteria>
MODEL_REGISTRY has a TypedDict-based schema, every entry carries `supports_thinking: bool`, the D-04 whitelist matches exactly, and an always-on test file enforces it.
</success_criteria>

<output>
After completion, create `.planning/phases/02-llm-eval-testing/02-02-SUMMARY.md` documenting: (a) count of entries, (b) count of thinkers, (c) line range where TypedDict class was inserted.
</output>
