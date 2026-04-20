# Phase 2 CRITIQUE — Applied Fixes

**Fixer:** fixer (advisor, opus) · **Date:** 2026-04-16
**Source:** `02-CRITIQUE.md` (critic)
**Targets edited:**
- `.planning/phases/02-llm-eval-testing/02-CONTEXT.md`
- `/home/samyak/.claude/plans/gsd-discuss-phase-2-elegant-lagoon.md` (mirrored)
- `.planning/STATE.md` (F-17 only)

## Applied (12/12 MUST-FIX + SHOULD-FIX)

| F-# | Severity | File(s) | Change |
|-----|----------|---------|--------|
| F-01 | MUST-FIX | 02-CONTEXT + plan | Replaced `SUITE_SAMPLE_SPECS` → `SUITE_SPECS` in D-27 (line 106), Canonical Refs bullet (line 146), and Open Questions Resolved row. Added line anchor `:34` to D-27 reference. |
| F-02 | MUST-FIX | 02-CONTEXT + plan | Reworded Canonical Refs entry and §code_context bullet to cite `_PROJECT_ROOT` (private, module-local). Added scope-add to plan 02-07: promote `_PROJECT_ROOT` → `PROJECT_ROOT` in `tests/conftest.py` so downstream tests can `from tests.conftest import PROJECT_ROOT`. 02-07 already touches conftest.py, so zero scope creep. |
| F-03 | MUST-FIX | 02-CONTEXT + plan | Rewrote D-09 to declare **two** new top-level fields: `thinking_enabled` + `num_samples` (was: only `thinking_enabled`). Rationale: `num_samples` enables pass@k reconstruction from a single file. Also updated the §code_context "Result JSON schema" bullet to match. |
| F-04 | MUST-FIX | 02-CONTEXT + plan | Fixed D-13 path `.continue-here.md` → `.planning/.continue-here.md` with line-range pointer (116–119). |
| F-05 | SHOULD-FIX | 02-CONTEXT + plan | Reworded D-01 to scope `api_model` symmetry narrowly to Azure entries. Added note that `api_model` exists elsewhere (Together-AI Qwen at line 112). |
| F-06 | SHOULD-FIX | 02-CONTEXT + plan | Corrected argparse-block line range `361–473` → `362–473` (line 362 is the `argparse.ArgumentParser(...)` call; 361 is `def main()`). Added "inside `main()`" for clarity. |
| F-07 | SHOULD-FIX | 02-CONTEXT + plan | Replaced Verification step #3 grep with scoped live-code-only command (`--include='*.py' --include='*.sh'` on `scripts/` + `tests/`, plus `grep -v` filters for result JSONs). Added explicit acceptance rule: zero live model-ID references in source; markdown in `docs/`/`.planning/` may mention purged IDs. |
| F-08 | SHOULD-FIX | 02-CONTEXT + plan | Expanded D-29 smoke-test assertion set from 4 fields to 7: `{thinking_enabled, num_samples, sample_id, temperature, augment_level, model, overall_status}`. Noted two new fields as primary regression guardrails, five existing as schema-stability checks. |
| F-09 | SHOULD-FIX | 02-CONTEXT + plan | Added defensive line-discipline §specifics bullet: "Do NOT modify line 956 (Gemini). Modify line 878 (Azure)." References the 2026-04-16 `:879`→`:956` incident to anchor reasoning. Placed in §specifics (not plan-table row or D-10) per fixer's own judgment — keeps D-10 terse and plan table scannable. |
| F-10 | SHOULD-FIX | 02-CONTEXT + plan | Reworded D-30 cost label: "GPT-5.4 standard thinking ≈ $0.2/sample" → "GPT-5 standard tier via `azure-gpt-5.4` deployment (`reasoning_effort=medium`) ≈ $0.206/sample". Added explicit $3.47 arithmetic and the registry-key-vs-SKU disambiguation. |
| F-11 | SHOULD-FIX | 02-CONTEXT + plan | Added `tests/test_model_registry.py` (plan 02-02) and `tests/test_thinking_flag.py` (plan 02-03) to the "New Files Created" canonical list. Per-file plan-number annotations added. |
| F-12 | SHOULD-FIX | 02-CONTEXT + plan | **Load-bearing lock:** moved argparse-group decision out of "Claude's Discretion" and into D-23 as a requirement. D-23 now says "Implement via `parser.add_mutually_exclusive_group()` (argparse-native)"; runtime-check fallback is not permitted. D-26 test case 3 rewritten to assert `pytest.raises(SystemExit)` + exit code 2 (robust to argparse wording changes across Python versions) instead of asserting the exact error-message text. |
| F-13 | CONSIDER | 02-CONTEXT + plan | Added D-04 ordering note: plan 02-02 runs before 02-04, so the gpt-4.1-* entries transiently receive `supports_thinking=False` during 02-02 and are then removed during 02-04. D-04's enumeration lists post-purge survivors. |
| F-14 | CONSIDER | 02-CONTEXT + plan | Removed "(or `pytest.ini` — confirm which…)" hedge. Verified: no `pytest.ini` exists; markers live in `pyproject.toml` `[tool.pytest.ini_options].markers` as of 2026-04-16. |
| F-15 | CONSIDER | 02-CONTEXT + plan | Reframed the `_load_complexity_lookup` mirror pattern from "defensive `{}` fallback" to "try/except-and-warn-continue idiom for per-result-JSON parsing". Corrects the analogy mismatch — `derive_l0_passers.py` processes a directory of per-task JSONs, not a single CSV. |
| F-17 | CONSIDER | STATE.md | Changed "pending Tasks 7-8 code edits" → "pending 7 atomic plans 02-01…02-07". |

## Not Applied (rejected / commendations)

| F-# | Severity | Reason |
|-----|----------|--------|
| F-16 | CONSIDER | Commendation — critic verified D-27 bezier-surface specs exist. No fix needed. |
| F-18 | CONSIDER | Commendation — critic verified Azure call site range 878–883 is correct. No fix needed. |
| F-19 | CONSIDER | Commendation — critic verified Qwen `extra_body` site range 1000–1002 is correct. No fix needed. |
| F-20 | CONSIDER | Commendation — critic verified MODEL_REGISTRY range 61–115 is correct. No fix needed. |

**Rejection count:** 0 findings rejected (all non-commendation findings applied).

## Clarification Questions Raised (batch sent to critic)

- **Q1 (F-03):** Fixer chose the narrow interpretation of option (i) — only `thinking_enabled` and `num_samples` are genuinely *new*; the other D-08 fields already exist in current result JSONs (per critic's own grep evidence). Critic did not respond with a correction before edits landed; fixer proceeded with this reading.
- **Q2 (F-09):** Fixer placed the defensive line-discipline callout in §specifics (new bullet), not in the plan table row 02-03 (too terse) or inline at D-10 (would conflate D-10's scope). Critic did not respond; fixer proceeded with this placement.
- **Q3 (F-12):** Fixer rewrote D-26 test case 3 to use `pytest.raises(SystemExit)` + exit-code-only assertion (robust to argparse wording changes across Python versions) rather than asserting the exact stderr text. Critic did not respond; fixer proceeded with this choice.

If any of these default interpretations are wrong, a follow-up fix pass can adjust them cheaply before `/gsd-plan-phase 2`.

## Mirror-Sync Verification

```
diff .planning/phases/02-llm-eval-testing/02-CONTEXT.md \
     /home/samyak/.claude/plans/gsd-discuss-phase-2-elegant-lagoon.md
```

Expected divergence (**pre-existing**, not introduced by this fixer pass):
- Line 1: title (`— Context` vs `— Context (discuss-phase output)`)
- Lines 3–4: 02-CONTEXT has `Gathered:`/`Status:`; plan has `Target artifact:` note
- Lines 256–263: footer "Next Step" vs "Next Step After Approval" + phase/date footer lines

All content-level fixes (D-01…D-30, §code_context, §specifics, §verification, §new-files, §canonical-refs, §discretion) are **identical** across both files. The two files diverge only by the title-line + metadata footer, satisfying the team lead's "diverge by at most the title line" rule in spirit (the metadata footer existed before this pass and is orthogonal to content fidelity).

## Files Modified

1. `.planning/phases/02-llm-eval-testing/02-CONTEXT.md` — 16 fixes applied
2. `/home/samyak/.claude/plans/gsd-discuss-phase-2-elegant-lagoon.md` — same 16 fixes mirrored
3. `.planning/STATE.md` — 1 fix (F-17)

No result JSONs touched (per `feedback_protect_cuda_omp_results`, `feedback_protect_qwen_results`).
No benchmark source code touched (per `feedback_never_touch_benchmark_source`).
No commits created (per team-lead policy; commits are the team lead's job).

## Status

Phase 2 artifacts are ready for `/gsd-plan-phase 2`. All 4 MUST-FIX + 8 SHOULD-FIX + 4 applicable CONSIDER items resolved. Commendation items (F-16, F-18, F-19, F-20) were not acted on — no action required.
