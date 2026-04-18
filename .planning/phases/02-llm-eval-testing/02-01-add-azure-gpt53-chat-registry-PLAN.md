---
phase: 02-llm-eval-testing
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - scripts/evaluation/llm_evaluate.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "MODEL_REGISTRY contains an entry keyed 'azure-gpt-5.4'"
    - "The entry has provider='azure' and supports_thinking=True"
    - "Existing Azure prefix-strip at line 861 resolves 'azure-gpt-5.4' → deployment 'gpt-5.4' with no code changes"
    - "MODEL_REGISTRY importability is preserved (no syntax/type errors at import time)"
  artifacts:
    - path: "scripts/evaluation/llm_evaluate.py"
      provides: "Updated MODEL_REGISTRY with azure-gpt-5.4 entry"
      contains: "azure-gpt-5.4"
  key_links:
    - from: "MODEL_REGISTRY['azure-gpt-5.4']"
      to: "client_az.chat.completions.create(...) at llm_evaluate.py:878"
      via: "prefix-strip model resolution at llm_evaluate.py:861"
      pattern: "azure-gpt-5\\.4"
---

<objective>
Add a new `azure-gpt-5.4` entry to `MODEL_REGISTRY` in `scripts/evaluation/llm_evaluate.py`.

Purpose: The Gal-approved canonical eval design (pass@3, L0, thinking=ON, reasoning_effort=medium) requires `azure-gpt-5.4` to be a registered model id. Without it, Phase 3 Phase A cannot launch against Le's Azure deployment. Committing this single entry first (before the schema-widening in 02-02 and the `gpt-4.1` purge in 02-04) gives `git bisect` a clean atomic step and ensures the Azure-entry set is never empty mid-commit (D-03).

Output: Single-line dict insertion into existing MODEL_REGISTRY.

Implements D-01, D-02, D-03.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-llm-eval-testing/02-CONTEXT.md
@scripts/evaluation/llm_evaluate.py
@.claude/rules/known-issues.md
@./CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Insert azure-gpt-5.4 MODEL_REGISTRY entry</name>
  <files>scripts/evaluation/llm_evaluate.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-01, D-02, D-03)
    - scripts/evaluation/llm_evaluate.py (lines 61-115, the MODEL_REGISTRY dict; line 861, Azure prefix-strip)
    - .claude/rules/known-issues.md
  </read_first>
  <action>
Edit `scripts/evaluation/llm_evaluate.py`:

1. Locate the MODEL_REGISTRY dict (lines 61-115).
2. Locate the existing `azure-gpt-4.1` entry (currently at lines 94-97 per CONTEXT D-11). Insert the new entry IMMEDIATELY AFTER the closing `}` of `azure-gpt-4.1` (so the two Azure entries are adjacent for readability; the purge in 02-04 will later remove `azure-gpt-4.1`, leaving `azure-gpt-5.4` as the sole Azure entry).

3. Insert this exact entry VERBATIM (per D-01/D-02):

```python
    "azure-gpt-5.4": {
        "provider": "azure",
        "supports_thinking": True,
        "notes": "Azure OpenAI GPT-5.4 reasoning deployment (Le) — requires AZURE_OPENAI_API_KEY+AZURE_OPENAI_ENDPOINT",
    },
```

4. Do NOT add an `api_model` field (D-01). The existing Azure prefix-strip at `llm_evaluate.py:861` (`model[len("azure-"):]` → `"gpt-5.4"`) handles deployment-name resolution. This matches the `azure-gpt-4.1` pattern.

5. Do NOT modify the type annotation on line 61 (`dict[str, dict[str, str]]` is about to be widened to TypedDict in plan 02-02; for this atomic commit the existing `bool` value in `supports_thinking` means Python accepts it at runtime but static type-checkers may warn — that is acceptable and transient).

6. Do NOT touch any other MODEL_REGISTRY entry in this plan. Adding `supports_thinking` to other entries is 02-02's scope.

7. Do NOT touch `llm_evaluate.py:878` (Azure call site) or `llm_evaluate.py:956` (Gemini safety line). Those are 02-03's scope.

8. Do NOT modify any imports or add TypedDict yet (02-02's scope).

Verify registry loads cleanly after the edit.
  </action>
  <verify>
    <automated>python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; e = MODEL_REGISTRY['azure-gpt-5.4']; assert e['provider'] == 'azure'; assert e['supports_thinking'] is True; assert 'AZURE_OPENAI_API_KEY' in e['notes']; print('OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -n '"azure-gpt-5.4"' scripts/evaluation/llm_evaluate.py` returns exactly one match.
    - `grep -n '"provider": "azure"' scripts/evaluation/llm_evaluate.py` returns at least two matches (`azure-gpt-4.1` still present at this stage + new `azure-gpt-5.4`).
    - `grep -n 'supports_thinking' scripts/evaluation/llm_evaluate.py` returns exactly one match (only the new entry carries it; 02-02 adds to others).
    - `grep -n 'api_model' scripts/evaluation/llm_evaluate.py` shows NO new line relative to pre-edit (only pre-existing Together-AI Qwen entry at line 112 retains `api_model`).
    - `python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; print(MODEL_REGISTRY['azure-gpt-5.4']['provider'])"` prints `azure`.
    - `python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; print(MODEL_REGISTRY['azure-gpt-5.4']['supports_thinking'])"` prints `True`.
    - Line 878 (Azure call site) and line 956 (Gemini `reasoning_effort="none"` safety line) are byte-for-byte unchanged — verify via `git diff scripts/evaluation/llm_evaluate.py` showing changes only in the MODEL_REGISTRY block.
  </acceptance_criteria>
  <done>New `azure-gpt-5.4` entry present in MODEL_REGISTRY with the exact three fields specified by D-02; no other lines in the file modified.</done>
</task>

</tasks>

<verification>
- `python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; assert 'azure-gpt-5.4' in MODEL_REGISTRY"` exits 0.
- `git diff --stat scripts/evaluation/llm_evaluate.py` reports ~5-6 lines added, 0 removed.
- No other files in the repo changed (`git status --porcelain` shows only `scripts/evaluation/llm_evaluate.py`).
</verification>

<success_criteria>
The MODEL_REGISTRY has a functional `azure-gpt-5.4` entry that (a) passes the D-02 field shape assertion and (b) is resolved by the existing `azure-` prefix-strip at line 861 to the Azure deployment name `gpt-5.4`.
</success_criteria>

<output>
After completion, create `.planning/phases/02-llm-eval-testing/02-01-SUMMARY.md` documenting the single insertion (line numbers before/after) and confirming `azure-gpt-4.1` still present (purge happens in 02-04).
</output>
