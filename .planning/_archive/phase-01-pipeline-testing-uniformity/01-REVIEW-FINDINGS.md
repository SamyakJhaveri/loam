# Phase 01 Plan Review — Findings

**Reviewer:** adversarial-reviewer (Sonnet 4.6)
**Date:** 2026-04-10
**Scope:** Plans 01-01 through 01-05
**Verdict:** NEEDS FIXES (7 issues found: 1 BLOCKER, 4 WARNINGs, 2 INFOs)

---

## Decision Coverage Matrix (D-01 through D-20)

| Decision | Plan | Task | Coverage |
|----------|------|------|----------|
| D-01 (test scope: 1 spec per suite, same 5 specs) | 01-02 | Task 1 | FULL |
| D-02 (new file: test_harness_integration.py) | 01-02 | Task 1 | FULL |
| D-03 (full pipeline: build → run → verify) | 01-02 | Task 1 | FULL |
| D-04 (KNOWN_FAIL → pytest.mark.skip via EXCLUDED_SPECS) | 01-02 | Task 1 | FULL |
| D-05 (project root auto-detected from conftest.py) | 01-02 | Task 1 | PARTIAL — see WARNING W-01 |
| D-06 (@pytest.mark.integration) | 01-02 | Task 1 | FULL |
| D-07 (EXCLUDED_SPECS in harness/constants.py) | 01-01 | Task 1 | FULL |
| D-08 (4 files → import from harness.constants) | 01-01 | Task 2 | FULL |
| D-09 (constants.py = single source of truth, sync with known-issues.md) | 01-01 | Task 1 | FULL |
| D-10 (analyze_harness_batch.py + delete analyze_rodinia_batch.py) | 01-03 | Tasks 1+2 | FULL |
| D-11 (output: results/harness/{suite}/) | 01-03 | Task 1 | FULL |
| D-12 (output files: {suite}_results.json + results_matrix_{suite}.md) | 01-03 | Task 1 | FULL |
| D-13 (quantitative_findings.py → per-suite dict) | 01-04 | Task 1 | PARTIAL — see BLOCKER B-01 |
| D-14 (classify_translation_pairs.py → --suite flag) | 01-04 | Task 2 | PARTIAL — see WARNING W-02 |
| D-15 (harness/ + scripts/evaluation/ → no suite hardcoding, verify only) | 01-04 | Task 3 | FULL |
| D-16 (test_campaign_classification.py with skip markers) | 01-02 | Task 2 | FULL |
| D-17 (campaign_for interface: record: dict → str) | 01-02 | Task 2 | FULL |
| D-18 (C2 logic: temp != 0.0 OR sample_id not None) | 01-02 | Task 2 | PARTIAL — see INFO I-01 |
| D-19 (test cases: c1={temp:0.0,sid:None}, c2={temp:0.7,sid:'s1'}) | 01-02 | Task 2 | FULL |
| D-20 (campaign_for lives in scripts/evaluation/campaign_utils.py) | 01-02 | Task 2 | FULL |

**Coverage summary:** 17/20 fully covered. 3 partially covered (see issues below).

---

## Requirements Coverage Matrix

| Phase 1 Requirement | Plan | Status |
|---------------------|------|--------|
| Spec loading works for all 5 suites (Phase 1a — already complete) | — | DONE (pre-existing) |
| Build works for 1+ program per suite per API | 01-02 | Covered by test_harness_integration.py |
| Run + verify works for all non-KNOWN_FAIL specs | 01-02 | Covered (5 smoke specs) |
| EXCLUDED_SPECS centralized as one importable constant | 01-01 | Covered |
| Suite-specific analysis code generalized (analyze_rodinia_batch.py replaced) | 01-03, 01-04 | Covered |
| No `if suite == "rodinia"` special-casing in pipeline code | 01-04 | Covered (Task 3 verifies harness + eval) |
| Unit tests cover EXCLUDED_SPECS filtering | 01-02 | Covered (test_excluded_specs_count) |
| Integration smoke tests cover 1+ spec per suite | 01-02 | Covered |
| Portability audit documented | 01-05 | Covered |

**All 9 Phase 1 requirements have covering plan tasks.**

---

## Issues

### BLOCKER B-01: Wrong line number guidance for rodinia_c1_total initialization in Plan 01-04

**Plan:** 01-04, Task 1
**Severity:** BLOCKER

**What the plan says:** "Somewhere above the loop (search for `rodinia_c1_total` initialization, likely around lines 3020-3040)"

**What the code actually shows:** `rodinia_c1_total = 0` is at **line 3005** of `quantitative_findings.py` (verified via grep). The plan's stated range (3020-3040) is off by 15-35 lines. The counter is part of a block at lines 3002-3008:

```python
kf_excluded_count = 0
pass_count_independent = 0
rodinia_c1_pass = 0
rodinia_c1_total = 0    # ← line 3005
status_counter: dict[str, int] = {}
level_counter: dict[str, int] = {}
direction_set: set[str] = set()
```

**Why this is a BLOCKER:** The plan instructs the implementer to search "around lines 3020-3040" and replace `rodinia_c1_total = 0` and `rodinia_c1_pass = 0` with `suite_c1_counts: dict[str, dict[str, int]] = {}`. But:
1. `rodinia_c1_pass = 0` cannot be fully removed — it is STILL REFERENCED in spot-check 5 (line 3089: `_spot("rodinia_c1_pass_count", rod_passes_expected, rodinia_c1_pass)`).
2. The plan's Step 3 does add `rodinia_c1_pass = suite_c1_counts.get("rodinia", {}).get("pass", 0)` before the spot-check, which preserves correctness — but ONLY if the implementer reads Step 3 carefully AND recognizes that `rodinia_c1_pass` needs to be a local re-derivation, not eliminated entirely.
3. The wrong line number range will cause the implementer to search the wrong area first.

**Fix required:**
- Update the `<action>` in Plan 01-04 Task 1 to give the correct line: "Find `rodinia_c1_total = 0` at line ~3005 (in a block starting with `kf_excluded_count = 0`)".
- Clarify that `rodinia_c1_pass` must NOT be deleted from the initialization block — instead, replace the block:
  ```python
  # OLD (lines ~3004-3005):
  rodinia_c1_pass = 0
  rodinia_c1_total = 0
  # NEW:
  rodinia_c1_total = 0  # REMOVE this line entirely
  # (rodinia_c1_pass = 0 is also removed and re-derived from dict in spot-check 5)
  suite_c1_counts: dict[str, dict[str, int]] = {}
  ```
  Then in spot-check 5 block, add the local re-derivation before the `_spot()` call.

---

### WARNING W-01: D-05 inaccuracy — conftest.py exposes `_PROJECT_ROOT` (private), not `PROJECT_ROOT`

**Plan:** 01-CONTEXT.md (D-05), 01-RESEARCH.md (Pattern 2), 01-02 Task 1
**Severity:** WARNING

**What the context/research claims:** D-05 says "Project root is auto-detected from `conftest.py` (existing `PROJECT_ROOT` constant)." Research Pattern 2 describes it as "VERIFIED: test_spec_loader_integration.py lines 34-39".

**What the code actually shows:** `conftest.py` exposes `_PROJECT_ROOT` (private, underscore-prefixed). There is NO public `PROJECT_ROOT` exported from conftest. Each test file defines its own `PROJECT_ROOT = Path("/home/samyak/Desktop/parbench_sam")` directly (confirmed in `test_spec_loader_integration.py` line 29).

**Why this matters:** If a developer reads D-05 literally and tries to `from conftest import PROJECT_ROOT`, it will fail with ImportError. Plan 01-02 Task 1 correctly handles this by copying the pattern from `test_spec_loader_integration.py` (hardcoded path), so the implementation plan is NOT broken. But D-05 in CONTEXT.md is misleading.

**Fix required:**
- Update D-05 wording in the `<read_first>` block of Plan 01-02 Task 1 to clarify: "Use the same hardcoded `PROJECT_ROOT = Path("/home/samyak/Desktop/parbench_sam")` pattern from `test_spec_loader_integration.py:29`. Note: conftest.py exposes `_PROJECT_ROOT` (private) — do not import from conftest."
- The plan's `<action>` already does the right thing; only the D-05 description (in context) is wrong.

---

### WARNING W-02: Plan 01-04 Task 2 underspecifies the function signature threading for `classify_translation_pairs.py`

**Plan:** 01-04, Task 2
**Severity:** WARNING

**What the plan says:** "If the display function is `display_results(rows)`, change its signature to `display_results(rows, suite_filter=None)` and call it as `display_results(rows, suite_filter=args.suite)`."

**What the code actually shows:** The function is named `print_summary(rows)` (verified — the file ends with `print_summary(rows)` called from `main()`). The "By Direction (Rodinia)" block is INSIDE `print_summary()` at lines 165-184. The `argparse` setup is in `main()` at line 187.

The plan uses conditional language ("If the display function is `display_results(rows)`") which is imprecise and could confuse an implementer who finds `print_summary` instead. The plan should use the actual function name.

**Additional issue:** The plan's Step 2 says "Find where the display/print function is called (the function that contains the 'By Direction' section). Pass the `args.suite` value to it." — but `main()` does NOT currently pass anything to `print_summary()`. The implementer needs to know that `main()` calls `print_summary(rows)` directly (no suite filter) and that call needs to change to `print_summary(rows, suite_filter=args.suite)`.

**Fix required:**
- Replace "If the display function is `display_results(rows)`" with "The display function is `print_summary(rows)` (line ~149)"
- Explicitly state that `main()` calls `print_summary(rows)` directly and the call must become `print_summary(rows, suite_filter=args.suite)`.

---

### WARNING W-03: Plan 01-04 Task 1 verify script has a logic bug

**Plan:** 01-04, Task 1 `<verify>` block
**Severity:** WARNING

**What the plan says:**
```python
assert 'rodinia_c1_pass' in content, 'rodinia_c1_pass used in spot-check 5 should still be referenced'
assert 'suite_c1_counts.get("rodinia"' in content or "suite_c1_counts.get('rodinia'" in content, 'Missing per-suite rodinia lookup'
```

**The issue:** After the edit, `rodinia_c1_pass` will appear in the file both as a local re-derivation (`rodinia_c1_pass = suite_c1_counts.get(...)`) AND in the `_spot()` call. The assertion `'rodinia_c1_pass' in content` will pass trivially. It does not verify that the OLD initialization (`rodinia_c1_pass = 0`) was actually removed. A partial edit (where the implementer only adds the new dict but forgets to remove the old `= 0` initialization) would pass this assertion.

**Fix required:** Add a negative assertion:
```python
assert 'rodinia_c1_total' not in content, 'Old rodinia_c1_total = 0 still present'
# Also verify the OLD literal initialization is gone:
lines = content.splitlines()
assert not any(l.strip() == 'rodinia_c1_pass = 0' for l in lines), 'Old rodinia_c1_pass = 0 still present'
```

---

### WARNING W-04: Plan 01-01 Task 2 verify script has a false-safety assertion

**Plan:** 01-01, Task 2 `<verify>` block
**Severity:** WARNING

**What the plan says:**
```python
assert 'frozenset({' not in content.split('from harness.constants')[0].split('EXCLUDED_SPECS')[-1] if 'EXCLUDED_SPECS' in content.split('from harness.constants')[0] else True, f'{f}: still has local definition'
```

**The issue:** This assertion only checks for `frozenset({` in the text *before* `from harness.constants`. But if the old `EXCLUDED_SPECS = frozenset({...})` block is not fully deleted (e.g., if only the import is added but the old definition remains AFTER the import line), this check misses it. A simpler and more reliable check would be:
```python
assert content.count('frozenset({') == 0, f'{f}: still has local frozenset definition'
```
But this also fails for files that use frozenset for OTHER purposes. The safest check is:
```python
import re
local_def = re.search(r'EXCLUDED_SPECS\s*[:=].*frozenset', content)
assert local_def is None, f'{f}: still has local EXCLUDED_SPECS frozenset definition'
```

**Fix required:** Replace the overly complex and fragile assertion with the regex-based check above.

---

### INFO I-01: D-18 C2 classification logic not validated in TDD test stubs

**Plan:** 01-02, Task 2; 01-CONTEXT.md D-18/D-19
**Severity:** INFO

**What D-18 says:** "C2 classification logic: `temperature != 0.0 OR sample_id is not None`. Either signal → C2."

**What the test covers:** Only two test cases per D-19:
- `{temperature: 0.0, sample_id: None}` → `'c1'` (both signals absent)
- `{temperature: 0.7, sample_id: 's1'}` → `'c2'` (both signals present)

**The gap:** Neither test case covers the OR logic explicitly. If someone implements `campaign_for()` as `temperature != 0.0 AND sample_id is not None` (AND instead of OR), both test cases still pass. The OR boundary conditions (`temp!=0.0 + sid=None` → c2, `temp=0.0 + sid='s1'` → c2) are explicitly deferred per CONTEXT.md.

This is accepted as-is per the deferred items, but it means the TDD tests do NOT fully lock the OR logic. Phase 2 must add the OR boundary tests before implementing to correctly TDD the logic.

**No fix required** — this is a known deliberate omission per CONTEXT.md. Flag for Phase 2 planning.

---

### INFO I-02: Plan 01-03 analyze_harness_batch.py uses hardcoded PROJECT_ROOT constant

**Plan:** 01-03, Task 1
**Severity:** INFO

**What the plan prescribes:** The new `analyze_harness_batch.py` should have:
```python
PROJECT_ROOT = Path("/home/samyak/Desktop/parbench_sam")
```

**The concern:** This mirrors the existing pattern in `analyze_rodinia_batch.py` and is consistent with all other analysis scripts. However, the portability audit (Plan 01-05) is supposed to document this as a known hardcoded path. The REQUIREMENTS.md says "Portability audit documented: hardcoded compiler paths acknowledged." Plan 01-05 covers this explicitly.

**The issue:** The hardcoded path is acceptable given the deferral decision, but Plan 01-03 could note that Plan 01-05 will document it. This creates a minor documentation gap — a reviewer seeing the new script in isolation won't know why the hardcoding is accepted.

**No fix required** — Plan 01-05 handles documentation. No code change needed.

---

## Wave Assignment and Dependency Check

| Plan | Wave | Depends On | Issues |
|------|------|-----------|--------|
| 01-01 | 1 | [] | None — correctly independent |
| 01-02 | 2 | ["01-01"] | Correct — needs harness/constants.py to exist |
| 01-03 | 1 | [] | None — correctly independent of 01-01 |
| 01-04 | 2 | ["01-01"] | Correct — Task 1 needs harness.constants import to already exist in quantitative_findings.py |
| 01-05 | 2 | ["01-01"] | Minor issue: portability audit reads harness files but is documentation-only; could be wave 1 |

**Wave 1 parallel conflict check:** Plans 01-01 and 01-03 both run in wave 1 with no dependencies. They touch DIFFERENT files (01-01: harness/constants.py + 4 analysis files; 01-03: analyze_harness_batch.py + delete analyze_rodinia_batch.py). NO file conflicts.

**Wave 2 parallel conflict check:** Plans 01-02, 01-04, and 01-05 all run in wave 2, all depending on 01-01. File conflict check:
- 01-02: tests/test_harness_integration.py, tests/test_campaign_classification.py
- 01-04: scripts/analysis/quantitative_findings.py, scripts/analysis/classify_translation_pairs.py
- 01-05: .planning/phases/.../portability-audit.md

No file conflicts. Safe to run in parallel.

**One missing dependency:** Plan 01-04 Task 1 action says "Do NOT change the `from harness.constants import EXCLUDED_SPECS` line (added by Plan 01)." This correctly assumes Plan 01-01 has already run. The `depends_on: ["01-01"]` captures this correctly. No issue.

---

## CLAUDE.md Compliance Check

| Rule | Plans Checked | Status |
|------|--------------|--------|
| `python3` not `python` | All verify blocks use `python3` | PASS |
| `from __future__ import annotations` | Plans 01-01, 01-02, 01-03 all specify it | PASS |
| Double quotes for strings | Code examples use double quotes consistently | PASS |
| `frozenset[str]` type annotation | Correctly used in Plan 01-01 | PASS |
| snake_case function names | All new functions follow pattern | PASS |
| Constants in UPPER_SNAKE_CASE | `EXCLUDED_SPECS`, `SUITE_SPECS`, `PROJECT_ROOT` | PASS |
| No `python` bare invocations | None found | PASS |

---

## Edge Cases and Execution Risks

1. **Plan 01-03 Task 2 uses `git rm`:** The action says `git rm scripts/analysis/analyze_rodinia_batch.py`. This is correct for deletion AND staging in git. But it will fail if the file has uncommitted changes. Since the file exists and is tracked, this should succeed. Low risk.

2. **Plan 01-02 conftest auto-skip logic:** The conftest skips integration tests when EITHER `rodinia/rodinia-src` OR `HeCBench-master` is absent. On the Linux GPU machine both exist, so integration tests run. On macOS, both absent, tests auto-skip. This is correct behavior and Plans handle it properly.

3. **Plan 01-02 Task 1 suite_spec fixture:** The fixture returns `(suite_name, loaded_spec_dict)` but the test function must unpack it correctly. The plan says `Takes suite_spec fixture (unpacks to suite, spec)`. This is correct syntactically in pytest if the fixture returns a tuple. No issue.

4. **`harness/__init__.py` is currently empty (just a comment).** Plan 01-01 explicitly says "Do NOT modify `harness/__init__.py`". This is correct — callers import directly via `from harness.constants import EXCLUDED_SPECS`. No issue.

5. **`scripts/analysis/quantitative_findings.py` is ~3085 lines.** The spot-check 5 block at lines 3085-3090 is tightly coupled to the counter variables at lines 3004-3005. The plan correctly identifies this coupling but gives wrong line guidance (see BLOCKER B-01).

---

## Fix Priority Summary

| ID | Severity | Plan | Fix Needed |
|----|----------|------|-----------|
| B-01 | **BLOCKER** | 01-04 Task 1 | Fix line number guidance (3005 not 3020-3040); clarify that rodinia_c1_pass needs local re-derivation not full elimination |
| W-01 | WARNING | 01-02 Task 1 | Add clarifying note that conftest._PROJECT_ROOT is private; action is already correct |
| W-02 | WARNING | 01-04 Task 2 | Replace "display_results" with actual function name "print_summary"; clarify main() call site |
| W-03 | WARNING | 01-04 Task 1 | Add negative assertion to verify script to catch partial edits |
| W-04 | WARNING | 01-01 Task 2 | Replace fragile verify assertion with regex-based check |
| I-01 | INFO | 01-02 Task 2 | No code fix; flag for Phase 2 to add OR boundary tests |
| I-02 | INFO | 01-03 Task 1 | No fix needed; portability audit covers this |

---

## Final Verdict

**NEEDS FIXES**

One BLOCKER (B-01) must be resolved before execution: the wrong line number range in Plan 01-04 Task 1 will cause the implementer to hunt in the wrong section of a 3085-line file, and the interaction between `rodinia_c1_pass = 0` initialization removal and its re-derivation in spot-check 5 is under-specified.

Four WARNINGs should be fixed to improve execution reliability (W-01 through W-04). Two INFOs are acknowledged non-issues.

Once B-01 and the WARNINGs are addressed, the plans are ready for execution.
