---
phase: 02-llm-eval-testing
plan: 04
type: execute
wave: 4
depends_on:
  - "02-02"
  - "02-03"
files_modified:
  - scripts/evaluation/llm_evaluate.py
  - scripts/evaluation/run_eval_batch.py
  - scripts/evaluation/analyze_eval.py
  - scripts/evaluation/test_generate_paper_figures.py
  - scripts/analysis/selfrepair_analysis.py
  - scripts/analysis/test_cross_model_comparison.py
  - scripts/analysis/token_analysis.py
  - scripts/generate_paper_figures.py
  - scripts/batch/archive/rerun_conjunction_eval.sh
  - tests/test_model_registry.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "`gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini` are absent from MODEL_REGISTRY"
    - "All 9 ParBench-owned files listed in D-12 are free of live `gpt-4.1*` model-ID references"
    - "`le_code/example_query.py` is UNTOUCHED (D-13)"
    - "`results/evaluation/azure-gpt-4.1/` and `results/evaluation/gpt-4.1-mini/` directories are UNTOUCHED on disk (D-15)"
    - "Test fixtures previously hardcoding `gpt-4.1-mini` as a model ID now use `azure-gpt-5.4` or `gpt-4o` with test intent preserved (D-14)"
    - "`tests/test_model_registry.py` whitelist updated to post-purge set"
  artifacts:
    - path: "scripts/evaluation/llm_evaluate.py"
      provides: "MODEL_REGISTRY without any gpt-4.1* entries"
      contains_not: "gpt-4.1"
    - path: "tests/test_model_registry.py"
      provides: "Updated EXPECTED_THINKERS set"
      contains: "EXPECTED_THINKERS"
  key_links:
    - from: "MODEL_REGISTRY after 02-04"
      to: "All downstream analysis + batch scripts"
      via: "Consistent model-ID whitelist"
      pattern: "azure-gpt-5\\.4|together-qwen|gpt-4o"
---

<objective>
Purge the three obsolete GPT-4.1 model IDs (`gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini`) from all ParBench-owned scripts, docs, and tests per D-11 and D-12. Result JSONs on disk (D-15) and the external `le_code/example_query.py` (D-13) are UNTOUCHED.

Purpose: Clears the field of dead model IDs before Phase 3 launches. Per `project_gpt_results_botched` memory, ALL GPT-4.1 mini results are invalid; per roadmap, GPT-4.1 is replaced by `azure-gpt-5.4`. Keeping dead IDs in the registry + analysis scripts is a source of confusion and silent mis-routing.

Implements D-11, D-12, D-13, D-14, D-15.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-llm-eval-testing/02-CONTEXT.md
@.planning/phases/02-llm-eval-testing/02-03-SUMMARY.md
@scripts/evaluation/llm_evaluate.py
@scripts/evaluation/run_eval_batch.py
@.claude/rules/known-issues.md
@./CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Remove gpt-4.1* entries from MODEL_REGISTRY and update the registry test</name>
  <files>scripts/evaluation/llm_evaluate.py, tests/test_model_registry.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-11, D-14, D-15)
    - scripts/evaluation/llm_evaluate.py (MODEL_REGISTRY post-02-02 state)
    - tests/test_model_registry.py (EXPECTED_THINKERS_POST_02_02 anchor)
    - .claude/rules/known-issues.md (reminder: result JSONs are append-only)
  </read_first>
  <action>
**Step 1 — Delete three MODEL_REGISTRY entries.** In `scripts/evaluation/llm_evaluate.py`:

1. Locate `"gpt-4.1-2025-04-14": { ... }` — delete the entire entry (key through closing `},`).
2. Locate `"azure-gpt-4.1": { ... }` — delete the entire entry.
3. Locate `"gpt-4.1-mini": { ... }` — delete the entire entry (if present).

Use `grep -n '"gpt-4\\.1' scripts/evaluation/llm_evaluate.py` to find all three. Delete each atomically. Preserve surrounding entry formatting + trailing comma hygiene.

**Step 2 — DO NOT touch `results/evaluation/azure-gpt-4.1/` or `results/evaluation/gpt-4.1-mini/`.** Those directories on disk are protected (D-15, `feedback_protect_cuda_omp_results`). No `rm`, no `git rm`, no rename.

**Step 3 — DO NOT touch `le_code/example_query.py`** (D-13 — external/untracked per `.planning/.continue-here.md` lines 116-119).

**Step 4 — Update `tests/test_model_registry.py` whitelist.** In the `EXPECTED_THINKERS_POST_02_02` set (anchor comment in 02-02), remove the two transient entries and rename the constant:

Replace:
```python
EXPECTED_THINKERS_POST_02_02 = {
    "azure-gpt-5.4",
    "o3-2025-04-16",
    "o4-mini-2025-04-16",
    "together-qwen-3.5-397b-a17b",
    # Transient — removed in 02-04:
    "gpt-4.1-2025-04-14",
    "azure-gpt-4.1",
}
```

With:
```python
# Post-02-04 authoritative thinking-capable set.
EXPECTED_THINKERS = {
    "azure-gpt-5.4",
    "o3-2025-04-16",
    "o4-mini-2025-04-16",
    "together-qwen-3.5-397b-a17b",
}
```

Update all references in the test file (find-replace `EXPECTED_THINKERS_POST_02_02` → `EXPECTED_THINKERS`). Update the test body comment to note 02-04 made this final.

Also remove the transient-handling `if k in MODEL_REGISTRY:` guard in `test_thinking_whitelist_matches_d04` — after the purge, every expected thinker MUST be in the registry (no more transient state). Rewrite:

```python
def test_thinking_whitelist_matches_d04():
    """Every expected thinker must be in the registry and set True.
    Every other registry entry must be False.
    """
    for k in EXPECTED_THINKERS:
        assert k in MODEL_REGISTRY, f"{k} must remain in registry post-02-04"
        assert MODEL_REGISTRY[k]["supports_thinking"] is True, f"{k} must be True"
    for k, v in MODEL_REGISTRY.items():
        if k not in EXPECTED_THINKERS:
            assert v["supports_thinking"] is False, f"{k} unexpectedly True; update D-04 whitelist?"
```
  </action>
  <verify>
    <automated>python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; bad = [k for k in MODEL_REGISTRY if 'gpt-4.1' in k]; assert not bad, bad; print('OK')" && python3 -m pytest tests/test_model_registry.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `grep -n '"gpt-4\\.1' scripts/evaluation/llm_evaluate.py` returns no matches.
    - `python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; print('gpt-4.1-mini' in MODEL_REGISTRY, 'azure-gpt-4.1' in MODEL_REGISTRY, 'gpt-4.1-2025-04-14' in MODEL_REGISTRY)"` prints `False False False`.
    - `ls results/evaluation/azure-gpt-4.1/ 2>&1 | head -1` shows contents unchanged (directory still exists on disk — if it existed pre-edit).
    - `ls results/evaluation/gpt-4.1-mini/ 2>&1 | head -1` shows contents unchanged.
    - `pytest tests/test_model_registry.py -v` passes all tests.
    - `grep -n 'EXPECTED_THINKERS_POST_02_02' tests/test_model_registry.py` returns no matches.
    - `grep -n 'EXPECTED_THINKERS' tests/test_model_registry.py` returns matches.
  </acceptance_criteria>
  <done>All three gpt-4.1 entries removed from MODEL_REGISTRY; registry test updated and passing; result-JSON directories on disk untouched.</done>
</task>

<task type="auto">
  <name>Task 2: Purge gpt-4.1* string references from 8 downstream files + update tests</name>
  <files>scripts/evaluation/run_eval_batch.py, scripts/evaluation/analyze_eval.py, scripts/evaluation/test_generate_paper_figures.py, scripts/analysis/selfrepair_analysis.py, scripts/analysis/test_cross_model_comparison.py, scripts/analysis/token_analysis.py, scripts/generate_paper_figures.py, scripts/batch/archive/rerun_conjunction_eval.sh</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-12, D-13, D-14)
    - Each file in the list above (read before editing)
    - .claude/rules/known-issues.md
    - Memory file: `feedback_protect_cuda_omp_results` (via MEMORY.md index)
  </read_first>
  <action>
For each of the 8 files below, (a) READ the file first, (b) identify every `gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini` occurrence via `grep -n`, (c) decide per-occurrence whether to DELETE (if the line's sole purpose is to reference the dead model) or REWRITE (if the line is a test fixture asserting behavior):

**Files to process (D-12 list, minus `le_code/example_query.py` per D-13):**

1. `scripts/evaluation/run_eval_batch.py` — likely a model whitelist or default list; delete dead IDs from list literals.
2. `scripts/evaluation/analyze_eval.py` — likely model-keyed aggregation defaults; delete dead IDs.
3. `scripts/evaluation/test_generate_paper_figures.py` — test fixtures; per D-14, rewrite `gpt-4.1-mini` → `azure-gpt-5.4` (for reasoning-capable test intent) OR `gpt-4o` (for standard-model test intent). Preserve what each test asserts.
4. `scripts/analysis/selfrepair_analysis.py` — likely model list for aggregation; delete dead IDs.
5. `scripts/analysis/test_cross_model_comparison.py` — test fixtures; per D-14, rewrite with replacement that matches test intent.
6. `scripts/analysis/token_analysis.py` — model-keyed token-counting dicts; delete dead IDs.
7. `scripts/generate_paper_figures.py` — figure generator model lists; delete dead IDs.
8. `scripts/batch/archive/rerun_conjunction_eval.sh` — archived batch script; delete or comment-out lines that invoke the dead models (this is an archive — if the whole script's purpose was to rerun gpt-4.1, replace the entire script body with a single-line comment "# Archived 2026-04-16 / plan 02-04: purged per D-11; retained as historical marker" — do NOT delete the file since the `batch/archive/` directory is an intentional history record).

**Decision rules for REWRITE vs DELETE (D-14):**

- If the reference is a test assertion, REWRITE: `gpt-4.1-mini` → `gpt-4o` (standard non-thinking model; preserves "test a non-thinking path" intent), OR `azure-gpt-5.4` (if the test needed a thinking-capable Azure model).
- If the reference is a list element (whitelist, default models, model loop), DELETE the list element.
- If the reference is a key in a dict used to look up model-specific results, DELETE the dict entry.
- If the reference is a display-string or comment, DELETE the line (documentation drift).
- If you cannot determine the purpose by local reading, read the enclosing function + the test that exercises it before changing anything.

**Hardcoded-fixture rewrites** (D-14): When rewriting, match test intent:
- Test asserts "reasoning model is handled correctly" → replacement = `azure-gpt-5.4`.
- Test asserts "standard OpenAI model is handled correctly" → replacement = `gpt-4o`.
- Test is agnostic (just needs a valid key) → replacement = `gpt-4o` (cheapest semantic).

**Do NOT:**
- Touch `le_code/example_query.py` (D-13).
- Touch ANY path under `results/evaluation/` (D-15).
- Touch markdown docs in `docs/` or `.planning/` or `.continue-here.md` — those are explicitly allowed to retain historical mentions per Verification rule #3 in CONTEXT.md.
- Silently rename a directory — the purge is about code + shell, not filesystem artifacts.

**Commit hygiene:** After editing each file, run `grep -n 'gpt-4\\.1' <file>` to confirm zero remaining matches in THAT file.
  </action>
  <verify>
    <automated>! grep -rn "gpt-4\\.1" scripts/ tests/ --include='*.py' --include='*.sh' | grep -v 'results/evaluation/' | grep -v 'batch_.*\\.json' | grep .</automated>
  </verify>
  <acceptance_criteria>
    - Final grep (from Verification rule #3 in CONTEXT.md §Verification): `grep -rn "gpt-4\\.1" scripts/ tests/ --include='*.py' --include='*.sh' | grep -v 'results/evaluation/' | grep -v 'batch_.*\\.json'` returns ZERO lines.
    - `ls le_code/example_query.py` shows the file still present (not deleted); `git status le_code/` shows no modification.
    - `ls results/evaluation/azure-gpt-4.1/ 2>&1 | head -5` shows original contents (if directory exists); `ls results/evaluation/gpt-4.1-mini/` likewise.
    - `git diff --stat scripts/batch/archive/rerun_conjunction_eval.sh` shows either a full-body replacement to a comment, or deletion of the gpt-4.1 invocation lines — NOT a file deletion.
    - `pytest scripts/evaluation/test_generate_paper_figures.py scripts/analysis/test_cross_model_comparison.py tests/test_model_registry.py -v` passes (test fixture rewrites preserve intent).
    - `grep -rln "gpt-4\\.1" .planning/ docs/` returns matches (historical mentions are expected and not touched).
  </acceptance_criteria>
  <done>All 8 ParBench-owned files free of live `gpt-4.1*` model-ID references; `le_code/` and `results/evaluation/` untouched; historical docs in `.planning/`/`docs/` retain mentions as allowed.</done>
</task>

</tasks>

<verification>
- `grep -rn "gpt-4\\.1" scripts/ tests/ --include='*.py' --include='*.sh' | grep -v 'results/evaluation/' | grep -v 'batch_.*\\.json'` → ZERO matches.
- `python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; assert not any('gpt-4.1' in k for k in MODEL_REGISTRY)"` exits 0.
- `pytest tests/test_model_registry.py tests/test_thinking_flag.py scripts/evaluation/test_generate_paper_figures.py scripts/analysis/test_cross_model_comparison.py -v` passes.
- `git status le_code/` shows no pending changes.
- `git status results/evaluation/` shows no pending changes.
</verification>

<success_criteria>
Zero live gpt-4.1 references under `scripts/` + `tests/` (per the CONTEXT.md §Verification grep). Result-JSON directories and `le_code/` untouched. Registry test updated to reflect post-purge whitelist.
</success_criteria>

<output>
After completion, create `.planning/phases/02-llm-eval-testing/02-04-SUMMARY.md` listing: (a) the 9 files touched with per-file line-delta counts, (b) the count of historical mentions retained in `.planning/`/`docs/` (proving the grep filter is scoped correctly), (c) confirmation that `le_code/example_query.py` and `results/evaluation/*gpt-4.1*` are byte-identical pre/post.
</output>
