# Implementation Prompt: Pipeline Audit Regex Combiner Fix

Copy everything below the line into a new Claude Code session.

---

## Task: Implement Pipeline Audit Fixes from Plan

Read the plan at `/home/samyak/.claude/plans/gentle-tinkering-planet.md` — it contains the full audit findings and implementation steps. Execute all 5 steps in order. ultrathink.

### Summary of what to implement:

**Step 1 — Fix regex combiner bug in `scripts/evaluation/llm_evaluate.py`:**
- In function `_build_cross_api_verify_spec()` at line ~1249, the pattern combiner wraps patterns as `(?:pattern)` which breaks when a pattern has inline `(?i)` flags (produces `(?:(?i)...)` which Python rejects).
- Add a `_wrap_pattern(p)` helper that detects leading `(?flags)` via `re.match(r'^\(\?([aimsux]+)\)', p)` and converts to scoped form `(?flags:rest)`. Non-flagged patterns keep the current `(?:p)` wrapping.
- Replace line 1249: `combined_pattern = "|".join(f"(?:{p})" for p in all_patterns)` with `combined_pattern = "|".join(_wrap_pattern(p) for p in all_patterns)`
- The helper should handle ALL inline flag types (`aimsux`), not just `(?i)`.

**Step 2 — Write unit test in `tests/test_regex_combiner.py`:**
- Import `_build_cross_api_verify_spec` and `_wrap_pattern` from `scripts/evaluation/llm_evaluate.py`
- Test that combining `(?i)(pass|correct)` with `Distance=` produces a valid regex
- Test that `(?i)` is scoped (only affects its own branch, not `Distance=`)
- Test that patterns without flags still work correctly

**Step 3 — Create read-only re-verification script `scripts/analysis/reverify_regex_bug.py`:**
- Scan `results/evaluation/together-qwen-3.5-397b-a17b/` for results with "Invalid regex" in `error_message`
- For each, rebuild the combined pattern using the fixed `_wrap_pattern()` logic
- Check `run_stdout_snippet` against the fixed pattern
- Report which results would flip from VERIFY_FAIL to PASS
- Expected: 3 flips (rodinia-nn-opencl-to-rodinia-nn-cuda L1, L3, L4)
- **DO NOT modify any result files** — results are immutable

**Step 4 — Update `.claude/rules/known-issues.md`:**
- Add "KNOWN_FAIL Inclusion Policy" section (see plan for exact text)
- Add "Pipeline Audit Results (2026-04-09)" section summarizing: 1 bug found (regex combiner), 0 pipeline bugs in core eval set, 347/1120 = 31.0% non-KNOWN_FAIL pass rate

**Step 5 — Run `/validate` before committing.**

### Key constraints:
- **NEVER modify result JSONs** in `results/evaluation/` — they are immutable
- **NEVER touch the running tmux sessions** (qwen_hecbench, qwen_small)
- The regex fix is in `scripts/evaluation/llm_evaluate.py` ONLY — do not change spec files
- The CFD OpenCL verify pattern is NOT a bug (kernel-only mode uses target patterns correctly) — do not change it
- All 8 specs with `(?i)` patterns are KNOWN_FAIL (except hecbench-crc64) — the fix prevents future issues

### Commit message suggestion:
```
fix(eval): scope inline regex flags in cross-API pattern combiner

The _build_cross_api_verify_spec() function combined source+target
verify patterns via (?:pattern1)|(?:pattern2). When a pattern contained
(?i) inline flags, wrapping in (?:...) placed the flags inside a
non-capturing group, causing Python re.compile() to reject the pattern.

Fix: detect leading inline flags and convert to scoped form (?i:...).
This scopes case-insensitivity to only the branch that needs it.

Found during pipeline audit of 1,248 Qwen results: 9 results affected
(all KNOWN_FAIL nn-opencl source), 3 would flip to PASS.
```
