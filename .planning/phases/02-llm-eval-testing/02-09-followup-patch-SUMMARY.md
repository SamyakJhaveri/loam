---
phase: 02-llm-eval-testing
plan: 09
plan_name: followup-patch
subsystem: scripts/evaluation, tests, docs, .planning
tags: [rename, pricing, typeddict, tmp_path, budget, audit-fix]
dependency_graph:
  requires:
    - 02-01-add-azure-gpt53-chat-registry
    - 02-02-supports-thinking-capability
    - 02-03-thinking-cli-flag
    - 02-04-purge-gpt41
    - 02-05-derive-l0-passers
    - 02-06-task-list-flag
    - 02-07-eval-e2e-smoke
    - 02-08-integration-smoke-and-handoff
  provides:
    - gpt-5.4 placeholder resolved to azure-gpt-5.3-chat throughout codebase
    - P0 critical fixes (tmp_path isolation, TypedDict semantics, pricing entries)
    - P1 quality fixes (line numbers, comments, budget text, test cleanup)
  affects:
    - tests/test_eval_e2e_smoke.py
    - tests/test_eval_integration_smoke.py
    - tests/test_model_registry.py
    - tests/test_derive_l0_passers.py
    - tests/test_run_eval_batch_task_list.py
    - tests/test_thinking_flag.py
    - tests/conftest.py
    - scripts/evaluation/llm_evaluate.py
    - scripts/evaluation/run_eval_batch.py
    - scripts/evaluation/analyze_eval.py
    - scripts/evaluation/test_generate_paper_figures.py
    - scripts/generate_paper_figures.py
    - scripts/analysis/token_analysis.py
    - scripts/analysis/selfrepair_analysis.py
    - scripts/analysis/test_cross_model_comparison.py
    - .claude/rules/evaluation.md
    - docs/neurips2026-experiment-plan.md
    - docs/neurips2026-gpt5-handoff.md
    - .planning/eval-selections/README.md
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md
    - .planning/phases/02-llm-eval-testing/02-03-thinking-cli-flag-SUMMARY.md
    - .planning/phases/02-llm-eval-testing/02-08-integration-smoke-and-handoff-SUMMARY.md
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
    - .planning/REQUIREMENTS.md
    - .planning/phases/02-llm-eval-testing/02-01-add-azure-gpt53-chat-registry-PLAN.md (renamed)
    - .planning/phases/02-llm-eval-testing/02-01-add-azure-gpt53-chat-registry-SUMMARY.md (renamed)
decisions:
  - "All azure-gpt-5.4 → azure-gpt-5.3-chat (Samyak decision 2026-04-17: placeholder resolved)"
  - "Historical PLAN/SUMMARY content left at gpt-5.4 except P1-5b/P1-7 factual line-number fixes"
  - "02-01 PLAN/SUMMARY filenames renamed (gpt54 → gpt53-chat); cross-ref pointers updated in live docs"
  - "l0_passers_gpt5.json → l0_passers_gpt5_3_chat.json in eval-selections/README.md and REQUIREMENTS.md"
  - "Pricing verified 2026-04-17: $1.75/$14 per 1M (not $2.50/$15 as placeholder assumed)"
  - "Budget: Gal approved $559 at pre-refresh pricing; refreshed ~$784 at verified rates; Samyak will escalate if realized spend trends above $559"
metrics:
  completed_date: 2026-04-17
---

# Plan 02-09 — Phase 2 Follow-Up Patch + GPT-5.4→5.3-Chat Rename

This patch applies the findings from the post-02-08 adversarial audit (critic agent) and
resolves the placeholder model identifier `azure-gpt-5.4` to `azure-gpt-5.3-chat` throughout
the codebase.

## Scope

Three parallel workstreams:

1. **P0 critical fixes** — bugs that would cause incorrect behavior in production
2. **P1 quality fixes** — stale references, misleading comments, test hygiene
3. **Rename** — global `azure-gpt-5.4` → `azure-gpt-5.3-chat` + pricing recompute at verified rates

## Placeholder resolution: gpt-5.4 → gpt-5.3-chat

Le confirmed 2026-04-17 that the Azure deployment is `gpt-5.3-chat` (GPT-5.3 Chat Global tier),
not `gpt-5.4`. The `azure-gpt-5.4` key used throughout Phase 2 was an explicit placeholder
(documented as such in all planning files since 2026-04-16).

**Token rewrites applied:**
- `azure-gpt-5.4` → `azure-gpt-5.3-chat` (registry key, CLI args, test fixtures, doc references)
- `GPT-5.4` → `GPT-5.3 Chat` (prose)
- `Azure GPT-5.4` → `Azure GPT-5.3 Chat` (prose)
- `gpt-5.4` → `gpt-5.3-chat` (deployment name references)
- `gpt54` → `gpt53-chat` (filename segments — Commit 4 git mv only)

**Pricing recompute (verified 2026-04-17 against provider pages):**
- Old placeholder rates: $2.50/1M input, $15.00/1M output
- Verified rates: $1.75/1M input, $14.00/1M output (GPT-5.3 Chat Global)
- Per-sample estimate: $0.28875 (was $0.3125 at unverified rates)
- Campaign total estimate: ~$784 for 2,714 samples (was ~$848 at placeholder rates)
- Gal approved $559 at pre-refresh pricing (2026-04-17); refreshed estimate is ~$225 above
  that figure. Samyak will escalate to Gal if realized spend trends materially above $559.

## Policy: historical files left at gpt-5.4

Phase 2 PLAN.md and SUMMARY.md files (02-01 through 02-08) record the state of the
codebase at the time they were written. Their content stays at `azure-gpt-5.4` as an
accurate historical record. Two exceptions (factual corrections, not rename):

- **P1-5b** (02-03 SUMMARY): line numbers `:903`/`:989` updated to `:905`/`:979` to
  reflect actual current grep results for the Azure and Gemini reasoning_effort call sites.
- **P1-7** (02-08 SUMMARY): test count `204 PASSED, 11 SKIPPED` corrected to
  `282 PASSED, 37 SKIPPED` (the 204/11 figure was the integration-only subset, not
  the full `pytest tests/ -q` run).

The 02-01 PLAN/SUMMARY **filenames** are renamed (gpt54 → gpt53-chat) per Samyak's
decision. Cross-ref pointer strings in live docs (ROADMAP.md, STATE.md, 02-CONTEXT.md)
and in historical SUMMARYs (02-08 dependency_graph) are updated to point to the new names.
The content of the 02-01 files themselves is preserved.

## Findings Addressed (P0 + P1)

### P0-1: tmp_path isolation in test_eval_e2e_smoke.py

`test_smoke_real_invocation` was passing `str(PROJECT_ROOT)` as `--project-root`, meaning
real LLM evaluation would write result JSONs to `results/evaluation/` in the live repo.
This violates the D-15 inviolable (never write to results/ in tests) and contaminates
production data.

**Fix:** Added `tmp_path: Path` fixture parameter. Changed `--project-root str(PROJECT_ROOT)`
to `--project-root str(tmp_path)`. Changed `out_dir` lookup from `PROJECT_ROOT / "results" ...`
to `tmp_path / "results" ...`.

### P0-2: TypedDict total=False semantic error in llm_evaluate.py

`ModelRegistryEntry` was declared `TypedDict, total=False` with `NotRequired[str]` on
`api_model`. The `total=False` makes ALL fields optional (including `provider`,
`supports_thinking`, `notes`), conflicting with the intent that those three are required.
`NotRequired` is only meaningful on a `total=True` TypedDict.

**Fix:** Changed to `TypedDict` (total=True by default). `provider`, `supports_thinking`,
`notes` are now required fields. `api_model` remains `NotRequired[str]`. Removed the
now-redundant inline `# required at runtime` / `# optional` comments.

### P0-3a: azure-gpt-5.3-chat missing from MODEL_PRICING (token_analysis.py)

`scripts/analysis/token_analysis.py:MODEL_PRICING` had no entry for `azure-gpt-5.3-chat`.
Token cost analysis would silently produce $0 cost for all GPT-5.3 Chat results.

**Fix:** Added `"azure-gpt-5.3-chat": {"input": 1.75, "output": 14.00, "display": "Azure GPT-5.3 Chat"}`.

### P0-3b: azure-gpt-5.3-chat missing from MODEL_DISPLAY (selfrepair_analysis.py)

`scripts/analysis/selfrepair_analysis.py:MODEL_DISPLAY` had no entry for the new model.
Self-repair analysis would use a fallback display name.

**Fix:** Added `"azure-gpt-5.3-chat": "Azure GPT-5.3 Chat"`.

### P1-4: Quick-Start commands stale in evaluation.md

The Quick-Start block still referenced `azure-gpt-4.1` (Phase 1 model) and lacked the
`--thinking on` flag required by the canonical config. Updated to reflect the Phase 2
canonical config: `azure-gpt-5.3-chat` for dry-run, `together-qwen-3.5-397b-a17b` with
`--thinking on` for batch examples.

### P1-5a: Stale line numbers in evaluation.md thinking-flag section

Line references for the Azure and Gemini `reasoning_effort` call sites were off by 2.
Updated `:903` → `:905` (Azure) and `:981` → `:979` (Gemini) at two locations in the
`--thinking` section of `evaluation.md`. Grep is authoritative; these numbers are live
as of 2026-04-17.

### P1-5b: Stale line numbers in 02-03 SUMMARY (factual fix, not rename)

The 02-03 SUMMARY recorded the Azure call site as `:903` and Gemini as `:989`. Current
grep returns `:905` and `:979`. Updated six line-number references in the SUMMARY body
and deviations section. This is a factual correction to match actual live code, not a
model-name rename.

### P1-6: Qwen notes and comment misleading in llm_evaluate.py

The Qwen registry entry `notes` said "thinking disabled" — which was the pre-02-03 state.
Post-02-03 the thinking flag is configurable. Updated to "thinking flag-driven, Plan 02-03".

The comment block above the `extra_body` call said "Explicitly disable thinking/reasoning
for Qwen 3.5 (thinking ON by default)" — also the pre-02-03 state. Updated to describe
the actual flag-driven behavior with reference to Plan 02-03.

### P1-7: Test count in 02-08 SUMMARY wrong (factual fix, not rename)

The 02-08 Self-Check recorded `204 PASSED, 11 SKIPPED` as the full test suite result.
That was the integration-only subset, not the full `pytest tests/ -q` run. Corrected to
`282 PASSED, 37 SKIPPED, 0 FAIL (pytest tests/ -q, 319 collected; 204/11 was the
integration-only subset)`.

### P1-8: Dead _PROJECT_ROOT alias in tests/conftest.py

`_PROJECT_ROOT = PROJECT_ROOT` was retained "for backward-compat with pre-02-07 tests"
per the original comment. Post-02-09 audit confirmed no remaining tests reference
`_PROJECT_ROOT`. The alias and its docstring qualifier are removed. The docstring is
tightened to remove the "Plan 02-07 also promoted" attribution.

### P1-9: Budget text in neurips2026-gpt5-handoff.md stale

The handoff runbook §7 still reflected the old unverified $2.50/$15 pricing and the
"pending Gal sign-off" status language. Updated to reflect:
- Verified pricing: $1.75/$14 per 1M
- Gal approved $559 on 2026-04-17 at pre-refresh pricing
- Refreshed campaign estimate: ~$784 (2,714 samples × $0.28875)
- Soft tripwire $600 retained (ROADMAP Phase 3 SC-5), reframed as "pause and consult
  Samyak" rather than "hard abort"
- Historical note: the $848 figure from unverified $2.50/$15 placeholder rates

## Deferred

### P2-10: No cross-suite assertion in test_model_registry.py

The thinkers set check in `test_model_registry.py` is correct but has no corresponding
assertion that `azure-gpt-5.3-chat` appears in `EXPECTED_THINKERS` AND has the matching
flag in `MODEL_REGISTRY`. This is redundant coverage — the existing tests cover both
individually. Deferred as low-value.

### P2-11: test_eval_integration_smoke.py pricing comment and runtime_cost_envelope

The `~$9/run` worst-case comment update was applied (at $14/1M for 80k output × some
factor). A more precise recompute (the doc cited $10/run at $15/1M for 80k × ~8 samples)
would give $8.75/run at $14/1M. The `~$9/run` approximation is acceptable.

### P2-12: No unit test for the P0-2 TypedDict fix

A test asserting `ModelRegistryEntry` behaves as `total=True` would catch regressions.
Deferred — mypy/pyright would catch this statically; adding a runtime test is low-value.

### P2-13: eval-selections/README.md passer_count/total_cells_evaluated example values

These are still illustrative extrapolations (287/522 from a 55% assumption). Not updated
here — they remain clearly labeled as estimates and will be replaced with real measurements
after Phase A runs.

## Note: 71c7957 / 90477ad landed --no-verify (policy: accepted)

Two commits in the Phase 2 sequence (71c7957 and 90477ad) were made with `--no-verify`,
bypassing the pre-commit validation gate. This is a known policy exception acknowledged
by Samyak: those commits were made under a "move fast" exception during initial Phase 2
plan execution. The 02-09 patch itself goes through the full validation gate (waves 1-3).

## Validation

After Phase A (all file writes), the following tests must pass before committing:
- `python3 -m pytest tests/ -q -m "not llm and not integration" --ignore=tests/test_harness_integration.py --ignore=tests/test_spec_loader_integration.py`
- `python3 -m pytest c_augmentation/test_transforms.py -q` (must be 15/15)

Full `/validate` (waves 1-3) run by team-lead before Phase B commit sequence.

## Commits in this patch

- **Commit 1:** fix+rename code (10 files) — P0-1/P0-2/P0-3a/P0-3b/P1-6 + rename in code+tests
- **Commit 2:** docs+rename (~14 files) — P1-4/P1-5a/P1-5b/P1-7/P1-9 + rename in live docs+planning
- **Commit 3:** cleanup conftest (1 file) — P1-8 dead alias removal
- **Commit 4:** git mv 02-01 plan filenames + cross-ref pointer updates in historical SUMMARYs
- **Commit 5:** this SUMMARY
