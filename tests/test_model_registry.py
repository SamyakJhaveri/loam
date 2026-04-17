"""Phase 2 / Plan 02-02: MODEL_REGISTRY capability-field invariants.

Enforces D-04 (every entry has `supports_thinking: bool`) and D-05
(no `model.startswith(...)` thinking-capability branching).
"""
from __future__ import annotations

import re
from pathlib import Path

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
    for match in re.finditer(r"model\.startswith\([^)]+\)", src):
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
