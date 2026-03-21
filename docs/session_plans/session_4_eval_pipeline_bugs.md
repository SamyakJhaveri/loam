# Session 4: Fix Eval Pipeline Bugs B1, B2, B6

> **Depends on:** Nothing (independent — can run in parallel with Sessions 2 or 3)
> **Blocks:** Session 5 (dashboard refresh)
> **Estimated time:** 20–30 minutes
> **Thinking level:** `think hard` (multi-file edits with cross-referencing)

---

## Objective

Three targeted bug fixes in the LLM evaluation pipeline scripts:
1. **B1:** Missing `kernel` field in result JSON (`llm_evaluate.py`)
2. **B2:** Markdown stats don't account for augment level in grouping key (`run_eval_batch.py`)
3. **B6:** `datetime.utcnow()` deprecated in Python 3.12+ (`llm_evaluate.py`)

---

## Claude Code Prompt

Copy-paste this into a fresh `/clear` session:

```
I need to complete Session 4 of the Sprint Audit Fix Plan: fix 3 eval pipeline bugs.

These are independent of Sessions 2-3 (the augmentation retest chain).

## Bug B1: Missing `kernel` field in result JSON

**File:** `scripts/evaluation/llm_evaluate.py`
**Location:** Around line 907-973 (the result dict construction)

**Problem:** The result dict has `source_spec` (e.g., "rodinia-nw-cuda") but no explicit
`kernel` field (e.g., "nw"). Downstream scripts (`analyze_eval.py`, `run_eval_batch.py`)
have to re-derive the kernel name from source_spec using helper functions.

**Fix:** Add a `kernel` field to the result dict, derived from the source_spec.

Read the file first to find:
1. The exact result dict construction (search for `result: dict` or `result = {`)
2. Where `source_id` / `source_spec` is set (it should be available before the dict)
3. The existing pattern for extracting kernel name — check `run_eval_batch.py:_extract_kernel()` (lines 39-51):
   ```python
   def _extract_kernel(r: dict) -> str:
       spec_id = r.get("source_spec", "?")
       parts = spec_id.split("-")
       if len(parts) < 3:
           return spec_id
       return "-".join(parts[1:-1])
   ```

Add `"kernel"` to the result dict using the same logic:
```python
# Before the result dict construction, extract kernel name:
_parts = source_id.split("-") if source_id and "-" in source_id else []
kernel_name = "-".join(_parts[1:-1]) if len(_parts) >= 3 else "?"

# Then in the result dict:
"kernel": kernel_name,
```

**Also update `run_eval_batch.py`** to use the stored field instead of re-parsing:
- Line 208: Change `_extract_kernel(r)` to `r.get("kernel") or _extract_kernel(r)` (backwards-compatible)
- Line 237-238: Same change in the sorting key

## Bug B2: Markdown stats overwrite on multi-level runs

**File:** `scripts/evaluation/run_eval_batch.py`
**Location:** Around lines 208-209 (the `_generate_markdown` function)

**Problem:** When running with `--augment-levels 0 1 2`, the markdown groups results
by `(model, kernel)` but ignores the augment level. Results at L0 get overwritten by L2
for the same kernel.

**Fix:** Include augment level in the grouping key.

Read the function `_generate_markdown()` (around line 201) carefully. Find where `by_model`
dict is built. The grouping key should be `(kernel, level)` not just `kernel`.

The fix likely involves:
1. Changing the dict structure from `by_model[model][kernel] = r` to `by_model[model][(kernel, level)] = r`
2. Updating the markdown table generation to show level columns or level-tagged rows
3. Making sure the summary stats are per-level, not aggregated

Think carefully about backwards compatibility — the function should still work correctly
when only one level is used (the common case).

## Bug B6: datetime.utcnow() deprecated

**File:** `scripts/evaluation/llm_evaluate.py`
**Location:** Line ~732

**Problem:** Python 3.12+ warns that `datetime.utcnow()` returns a naive datetime.
The correct modern approach uses timezone-aware datetimes.

**Fix:**
```python
# BEFORE (deprecated):
timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# AFTER (correct):
timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
```

Search for ALL uses of `utcnow()` in the file — there may be more than one.
Also check `run_eval_batch.py` and `analyze_eval.py` for the same pattern.

## Verification

1. **B1 check:** Read an existing result JSON to see current schema:
   ```bash
   ls results/evaluation/
   ```
   Find a result file and confirm `kernel` field is NOT there currently.
   Then do a dry conceptual check: if `source_spec = "rodinia-nw-cuda"`,
   the kernel extraction should produce `"nw"`.

2. **B2 check:** Read the `_generate_markdown` function after your edit.
   Mentally trace through: if results contain entries for L0 and L2 of the same kernel,
   do they appear as separate rows/columns? Or does L2 overwrite L0?

3. **B6 check:**
   ```bash
   source env_parbench/bin/activate
   python3 -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"
   ```
   Should print current UTC time without warnings.

4. **Import check:**
   ```bash
   python3 -c "from scripts.evaluation.llm_evaluate import evaluate_translation; print('OK')"
   ```
   Or if that doesn't work due to module structure:
   ```bash
   python3 -c "import scripts.evaluation.llm_evaluate; print('OK')"
   ```

5. **No regressions:**
   ```bash
   grep -rn "utcnow" scripts/evaluation/
   ```
   Should return nothing after the fix.

## Commit and Push

Commit ONLY after ALL verification passes. Then push immediately:

```
Fix eval pipeline bugs B1 (kernel field), B2 (level key), B6 (utcnow)

- B1: Add explicit "kernel" field to result JSON in llm_evaluate.py
  (downstream scripts no longer need to re-derive from source_spec)
- B2: Include augment_level in markdown grouping key in run_eval_batch.py
  (multi-level runs no longer overwrite each other in summary tables)
- B6: Replace deprecated datetime.utcnow() with datetime.now(timezone.utc)
```

```bash
git push origin main
```
```

---

## Files Reference

### `scripts/evaluation/llm_evaluate.py`

| Location | Bug | What Changes |
|----------|-----|-------------|
| ~line 732 | B6 | `datetime.utcnow()` → `datetime.now(datetime.timezone.utc)` |
| ~line 907-973 | B1 | Add `"kernel": kernel_name,` to result dict |

### `scripts/evaluation/run_eval_batch.py`

| Location | Bug | What Changes |
|----------|-----|-------------|
| lines 39-51 | (reference) | `_extract_kernel()` helper — keep for backwards compat |
| ~line 208 | B1+B2 | Use `r.get("kernel")` + include level in grouping |
| ~line 237-238 | B1 | Use stored kernel field in sort key |
| `_generate_markdown()` | B2 | Level-aware grouping and table generation |

### `scripts/evaluation/analyze_eval.py`

| Location | Bug | What Changes |
|----------|-----|-------------|
| ~line 150 | (check) | Already has `r.get("kernel", "?")` fallback — no change needed |

### Existing Result JSON Schema (no `kernel` field)

From `results/evaluation/azure-gpt-4.1/rodinia-kmeans-cuda-to-rodinia-kmeans-omp.json`:
```json
{
  "source_spec": "rodinia-kmeans-cuda",
  "target_spec": "rodinia-kmeans-omp",
  "model": "azure-gpt-4.1",
  "augment_level": 0,
  "timestamp": "2026-03-19T...",
  ...
}
```
Note: no `"kernel"` field exists currently.

## Design Considerations

### B2 Approach Options

**Option A (minimal):** Keep `by_model[model][kernel]` but make it `by_model[model][kernel][level]`:
- Markdown table gets level sub-columns
- More complex rendering but preserves per-kernel grouping

**Option B (simpler):** Make the grouping key `f"{kernel}_L{level}"`:
- Flat structure, one row per kernel-level combo
- Simpler implementation but longer tables

**Option C (recommended):** Separate tables per level:
- Each level gets its own summary table
- Matches the augmentation retest output format
- Easiest to compare across levels

Choose the approach that matches the existing markdown format most closely.
Read the current `_generate_markdown()` output to decide.

## Success Criteria

- [ ] `kernel` field appears in result dict construction
- [ ] `run_eval_batch.py` uses stored kernel field (with fallback)
- [ ] Multi-level grouping prevents overwrite
- [ ] No `utcnow()` calls remain in `scripts/evaluation/`
- [ ] Import checks pass
- [ ] Verified, committed, and pushed to remote
